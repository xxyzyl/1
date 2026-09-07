#!/usr/bin/env python3
"""Check declared shared resources for alternative life-project combinations.

No scheduling, life scoring, empirical verification, authorization, or actions.
Only one explicitly bounded period is accepted. Unknown amounts stay unknown.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, '重复JSON字段：' + key)
        result[key] = value
    return result


def parse_record(text):
    return json.loads(text, parse_float=Decimal, object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('不接受' + value)))


def amount(value, field):
    if value is None:
        return None
    require(type(value) in (int, Decimal), field + '须为非负数或null；不接受布尔值或数字字符串')
    if isinstance(value, Decimal):
        require(value.is_finite(), field + '不能为NaN或无穷')
    require(value >= 0, field + '不能为负数')
    return Fraction(value)


def render(value):
    if value is None:
        return None
    with localcontext() as ctx:
        ctx.prec = len(str(abs(value.numerator))) + len(str(value.denominator)) + 10
        return format(Decimal(value.numerator) / Decimal(value.denominator), 'f')


def index(items, label, allow_empty=False):
    require(isinstance(items, list) and (allow_empty or items), label + '须为列表，且除actions外不能为空')
    result = {}
    for item in items:
        require(isinstance(item, dict) and nonempty(item.get('id')), label + '每项须有id')
        require(item['id'] not in result, label + '存在重复id：' + item['id'])
        result[item['id']] = item
    return result


def check(record):
    require(isinstance(record, dict), '根节点须为对象')
    require(record.get('architecture') == '4.0', 'architecture须为4.0')
    require(nonempty(record.get('snapshot_id')), '须有snapshot_id')
    require(type(record.get('revision')) is int and record['revision'] > 0, 'revision须为正整数')
    period = record.get('period')
    require(isinstance(period, dict), '须明确period')
    for field in ('id', 'description', 'timezone'):
        require(nonempty(period.get(field)), 'period.' + field + '须为非空文本')
    budgets = index(record.get('resources'), 'resources')
    actions = index(record.get('actions'), 'actions', allow_empty=True)
    scenarios = index(record.get('scenarios'), 'scenarios')
    numeric = {}
    for key, resource in budgets.items():
        for field in ('name', 'unit', 'source'):
            require(nonempty(resource.get(field)), key + '.' + field + '须为非空文本')
        numeric[key] = {}
        for field in ('capacity', 'baseline', 'reserve'):
            require(field in resource, key + '缺少' + field + '；未知应显式写null')
            numeric[key][field] = amount(resource[field], key + '.' + field)
    demands = {}
    committed = set()
    domains = {f'D{i:02d}' for i in range(1, 10)}
    for key, action in actions.items():
        require(nonempty(action.get('description')), key + '缺少description')
        require(isinstance(action.get('owner_domain'), str) and action['owner_domain'] in domains, key + '主责领域须为D01—D09')
        affected = action.get('affected_domains')
        require(isinstance(affected, list) and all(isinstance(d, str) and d in domains for d in affected), key + '影响领域不合法')
        require(len(set(affected)) == len(affected), key + '影响领域重复')
        require(isinstance(action.get('status'), str) and action['status'] in {'committed', 'proposed'}, key + 'status须为committed或proposed')
        if action['status'] == 'committed':
            committed.add(key)
        demand = action.get('demand')
        require(isinstance(demand, dict) and set(demand) == set(budgets), key + '须逐项声明全部资源需求；未知用null，无需用0')
        demands[key] = {r: amount(demand[r], key + '.' + r) for r in budgets}
    results = []
    for key, scenario in scenarios.items():
        chosen = scenario.get('action_ids')
        require(isinstance(chosen, list) and all(isinstance(a, str) and a in actions for a in chosen), key + '引用未知行动')
        require(len(set(chosen)) == len(chosen), key + '同一行动不能重复计入')
        require(committed.issubset(set(chosen)), key + '遗漏已有承诺；须先在真实记录中处理承诺变更')
        totals = []
        for resource_id, resource in budgets.items():
            values = numeric[resource_id]
            unknown = [field for field in ('capacity', 'baseline', 'reserve') if values[field] is None]
            unknown += [a for a in chosen if demands[a][resource_id] is None]
            terms = [values['baseline'], values['reserve']] + [demands[a][resource_id] for a in chosen]
            known_minimum = sum((v for v in terms if v is not None), Fraction(0))
            capacity = values['capacity']
            if capacity is not None and known_minimum > capacity:
                status = '资源冲突'
            elif unknown:
                status = '待补资源数据'
            else:
                status = '资源可行'
            totals.append({'resource_id': resource_id, 'unit': resource['unit'], 'status': status,
                           'capacity': render(capacity), 'known_minimum_demand': render(known_minimum),
                           'total_demand': None if any(v is None for v in terms) else render(known_minimum),
                           'remaining': None if unknown else render(capacity - known_minimum),
                           'unknown_fields_or_actions': unknown})
        statuses = {item['status'] for item in totals}
        status = '资源冲突' if '资源冲突' in statuses else ('待补资源数据' if '待补资源数据' in statuses else '资源可行')
        results.append({'scenario_id': key, 'status': status, 'resources': totals})
    serialized = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':'), default=str)
    return {'snapshot_id': record['snapshot_id'], 'revision': record['revision'],
            'input_fingerprint': hashlib.sha256(serialized.encode()).hexdigest(),
            'period': period, 'scenarios': results,
            'scope': '仅核算声明的单周期资源；不是建议通过、授权、事实核实、日历排程或实际执行。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    try:
        data = parse_record(args.record.read_text(encoding='utf-8'))
        result = check(data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print('资源记录无效：' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
