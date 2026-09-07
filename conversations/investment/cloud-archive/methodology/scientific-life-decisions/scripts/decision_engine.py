#!/usr/bin/env python3
"""Validate a declared decision record and derive workflow readiness, not truth or permission."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

STAGES = {f'S{i}' for i in range(1, 9)}
RECOMMENDATIONS = {'待补证', '条件建议', '建议可供选择'}
CHOICES = {'未知', '未决定', '已决定', '暂缓'}
EXECUTIONS = {'未知', '未开始', '执行中', '已暂停', '已完成', '已停止'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def string(value):
    return isinstance(value, str) and bool(value.strip())


def meaningful(value):
    return string(value) and value.strip() not in {'未知', '待确认', '待填写', 'TODO', 'TBD', '填写实际记录编号', '未提供', '未说明', '不详', '待补充', '待查', '暂无', '无', '...', '-'}


def fingerprint(record):
    data = {key: record[key] for key in ('problem', 'evidence', 'options', 'gaps')}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def review_fingerprint(record):
    recommendation = {key: value for key, value in record['recommendation'].items() if key != 'status'}
    data = {'inputs': fingerprint(record), 'comparison': record['comparison'], 'recommendation': recommendation}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def selection_fingerprint(record):
    chosen = set(record['user_choice']['option_ids'])
    data = {'goal': record['problem']['goal'], 'constraints': record['problem']['constraints'],
            'selected_options': [item for item in record['options'] if item['id'] in chosen]}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def schema(record):
    require(isinstance(record, dict), '根节点必须为对象')
    require(record.get('protocol') == '3.0', 'protocol必须为3.0')
    require(meaningful(record.get('decision_id')), '缺少实际decision_id')
    require(type(record.get('revision')) is int and record['revision'] > 0, 'revision必须为正整数')
    for key in ('problem', 'comparison', 'review', 'recommendation', 'user_choice', 'execution'):
        require(isinstance(record.get(key), dict), f'{key}必须为对象')
    for key in ('evidence', 'options', 'gaps'):
        require(isinstance(record.get(key), list), f'{key}必须为列表')
    problem = record['problem']
    for key in ('question', 'goal', 'source'):
        require(isinstance(problem.get(key), str), f'problem.{key}必须为文本')
    require(isinstance(problem.get('constraints'), list), 'problem.constraints必须为列表')
    indexes = {}
    for key, items in [('constraints', problem['constraints']), ('evidence', record['evidence']), ('options', record['options'])]:
        indexes[key] = {}
        for item in items:
            require(isinstance(item, dict) and string(item.get('id')), f'{key}每项须有id')
            require(item['id'] not in indexes[key], f'{key}存在重复id：{item["id"]}')
            indexes[key][item['id']] = item
    for item in problem['constraints']:
        require(string(item.get('description')) and string(item.get('source')), '硬约束需有description和source')
    for item in record['evidence']:
        require(item.get('status') in {'用户陈述', '已核实', '假设', '待核实'}, '证据status不合法')
        require(type(item.get('decisive')) is bool, '证据decisive须为布尔值')
        for key in ('source', 'date', 'checked_at'):
            require(isinstance(item.get(key), str), f'证据{key}须为文本；缺失可显式填写未知')
    for item in record['options']:
        require(string(item.get('description')), '方案需有description')
        checks = item.get('constraint_checks')
        require(isinstance(checks, dict) and set(checks) == set(indexes['constraints']), '每个方案必须逐项覆盖全部硬约束')
        require(all(v in {'满足', '不满足', '未知'} for v in checks.values()), '约束检查取值不合法')
    for item in record['gaps']:
        require(isinstance(item, dict) and string(item.get('description')), '缺口须有description')
        require(item.get('stage') in {'S1', 'S2', 'S3', 'S4', 'S5'}, '建议缺口stage必须为S1—S5；授权与执行单独记录')
        require(item.get('severity') in {'阻断', '条件'}, '缺口severity不合法')
        require(type(item.get('resolved')) is bool, '缺口resolved须为布尔值')
        if item['resolved']:
            require(string(item.get('resolution')), '已解决缺口需写明resolution及依据')
    for section in ('comparison', 'review'):
        item = record[section]
        require(type(item.get('revision')) is int and item['revision'] >= 0, f'{section}.revision须为非负整数')
        require(isinstance(item.get('artifact'), str), f'{section}.artifact须为文本')
        require(isinstance(item.get('input_fingerprint'), str), f'{section}.input_fingerprint须为文本')
    comparison = record['comparison']
    for key in ('method', 'strongest_objection'):
        require(isinstance(comparison.get(key), str), f'comparison.{key}须为文本')
    for key in ('conditions', 'reversal_conditions'):
        require(isinstance(comparison.get(key), list) and all(meaningful(x) for x in comparison[key]), f'comparison.{key}须为具体文本的列表')
    for section, field, allowed in [('comparison', 'option_ids', indexes['options']), ('comparison', 'evidence_ids', indexes['evidence']), ('recommendation', 'option_ids', indexes['options']), ('user_choice', 'option_ids', indexes['options'])]:
        ids = record[section].get(field)
        require(isinstance(ids, list) and all(string(x) for x in ids), f'{section}.{field}须为ID列表')
        require(len(ids) == len(set(ids)) and all(x in allowed for x in ids), f'{section}.{field}有重复或不存在的引用')
    require(type(record['review'].get('completed')) is bool, 'review.completed须为布尔值')
    require(isinstance(record['review'].get('target_fingerprint'), str), 'review.target_fingerprint须为文本')
    require(record['review'].get('mode') in {'主智能体自审', '子智能体复核', '外部专业复核'}, 'review.mode不合法')
    require(record['recommendation'].get('status') in RECOMMENDATIONS, '建议状态仅允许待补证、条件建议、建议可供选择')
    require(record['user_choice'].get('status') in CHOICES, '用户选择状态不合法')
    require(record['execution'].get('status') in EXECUTIONS, '执行状态不合法')
    choice = record['user_choice']
    if choice['status'] == '已决定':
        require(bool(choice['option_ids']) and meaningful(choice.get('source')), '已决定需有真实选择及来源')
        require(type(choice.get('revision')) is int and 0 < choice['revision'] <= record['revision'], '已决定需记录当时输入版本，且不能来自未来版本')
        require(isinstance(choice.get('selection_fingerprint'), str), '已决定需记录selection_fingerprint')
    else:
        require(not choice['option_ids'], '未决定或暂缓时不可填写已选方案')
    execution = record['execution']
    if execution['status'] not in {'未知', '未开始'}:
        require(meaningful(execution.get('action_record')), '实际执行状态须有行动记录')
    return indexes


def evaluate(record):
    indexes = schema(record)
    blocking, conditional = [], []

    def block(stage, reason):
        blocking.append({'stage': stage, 'reason': reason})

    for key in ('question', 'goal', 'source'):
        if not meaningful(record['problem'][key]):
            block('S1', f'问题定义缺少{key}')
    for gap in record['gaps']:
        if not gap['resolved']:
            (blocking if gap['severity'] == '阻断' else conditional).append({'stage': gap['stage'], 'reason': gap['description']})
    if not record['evidence']:
        block('S2', '没有证据或用户陈述记录')
    if not record['options']:
        block('S3', '没有真实备选方案')
    comparison, review = record['comparison'], record['review']
    current_fingerprint = fingerprint(record)
    if comparison['revision'] != record['revision']:
        block('S4', '比较结果不属于当前输入版本')
    if comparison['input_fingerprint'] != current_fingerprint:
        block('S4', '输入内容已变化或尚未绑定，需核对比较结果')
    for key in ('method', 'artifact', 'strongest_objection'):
        if not meaningful(comparison[key]):
            block('S4', f'比较缺少{key}')
    if not comparison['reversal_conditions']:
        block('S4', '缺少反转条件或结论不敏感的具体解释')
    if set(comparison['option_ids']) != set(indexes['options']):
        block('S4', '比较未覆盖全部备选及其排除理由')
    if len(record['options']) == 1 and not string(comparison.get('single_option_reason')):
        block('S3', '仅有一个方案时须解释其他路径为何不可行')
    if not comparison['evidence_ids']:
        block('S2', '比较没有关联证据')
    for evidence in record['evidence']:
        if evidence['decisive'] and evidence['id'] not in comparison['evidence_ids']:
            block('S2', f'决定性证据{evidence["id"]}未纳入比较，不能跳过其影响')
    for eid in comparison['evidence_ids']:
        evidence = indexes['evidence'][eid]
        if evidence['decisive'] and evidence['status'] in {'假设', '待核实'}:
            conditional.append({'stage': 'S2', 'reason': f'{eid}为未确定的关键前提'})
        if evidence['decisive'] and not meaningful(evidence['source']):
            block('S2', f'{eid}缺少可定位的关键来源')
        if evidence['decisive'] and evidence['status'] == '已核实' and not meaningful(evidence['checked_at']):
            block('S2', f'{eid}未记录实际查阅日期')
    feasible = [key for key, option in indexes['options'].items() if all(x == '满足' for x in option['constraint_checks'].values())]
    recommended = record['recommendation']['option_ids']
    if not recommended:
        block('S3', '尚无有具体内容的建议选项')
    for oid in recommended:
        for cid, state in indexes['options'][oid]['constraint_checks'].items():
            if state != '满足':
                block('S4', f'建议方案{oid}的硬约束{cid}为{state}')
    if conditional and not comparison['conditions']:
        block('S4', '关键假设或条件缺口尚未转成明确成立条件')
    if review['revision'] != record['revision']:
        block('S5', '复核不属于当前输入版本')
    if review['input_fingerprint'] != current_fingerprint:
        block('S5', '输入内容已变化或尚未绑定，需重新核对受影响的复核项')
    if review['target_fingerprint'] != review_fingerprint(record):
        block('S5', '比较或建议对象已变化，旧复核不能用于当前建议')
    if not review['completed'] or not meaningful(review['artifact']):
        block('S5', '当前复核尚未完成或缺少实际产物')
    if review.get('mode') == '子智能体复核' and not meaningful(review.get('task_id')):
        block('S5', '子智能体复核缺少真实任务ID')
    status = '待补证' if blocking else '条件建议' if conditional or comparison['conditions'] else '建议可供选择'
    claimed = record['recommendation']['status']
    rank = {'待补证': 0, '条件建议': 1, '建议可供选择': 2}
    issues = []
    if rank[claimed] > rank[status]:
        issues.append(f'声明的建议状态超出记录支持范围：{claimed} > {status}')
    if claimed == '条件建议' and not comparison['conditions']:
        issues.append('声明条件建议却未列出成立条件')
    choice, execution = record['user_choice'], record['execution']
    execution_issues = []
    if choice['status'] == '已决定' and choice['selection_fingerprint'] != selection_fingerprint(record):
        execution_issues.append('用户选择对应的目标、约束或方案内容已变化/未绑定；核对旧选择和已有授权是否仍适用，不能只沿用方案ID')
    for oid in choice['option_ids']:
        if oid not in feasible:
            execution_issues.append(f'用户已选方案{oid}有未满足或未知的硬约束，需回到取舍环节核对')
    if execution['status'] not in {'未知', '未开始'} and not meaningful(execution.get('authorization_source')):
        issues.append('执行记录缺少对应的已有授权来源；不能据此推定有权限')
    next_stage = min((x['stage'] for x in blocking), default='S6')
    if not blocking and choice['status'] == '已决定' and not execution_issues:
        next_stage = 'S8' if execution['status'] in {'已完成', '已停止'} else 'S7'
    if not blocking and choice['status'] == '暂缓':
        next_stage = 'S6'
    return {'record_valid': not issues, 'supported_recommendation_status': status,
            'claimed_recommendation_status': claimed, 'feasible_option_ids': feasible,
            'blocking_issues': blocking, 'conditional_issues': conditional,
            'record_issues': issues, 'next_stage': next_stage,
            'execution_issues': execution_issues,
            'user_choice': choice['status'], 'execution_status': execution['status'],
            'note': '只检查声明的记录与状态一致性；不验证事实，不创建授权，不执行现实动作。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--fingerprint', action='store_true', help='Print input fingerprint only; this does not complete comparison or review')
    group.add_argument('--review-fingerprint', action='store_true', help='Print fingerprint for current comparison and proposed options; this does not perform review')
    group.add_argument('--selection-fingerprint', action='store_true', help='Print selected-content fingerprint; this does not create a user decision or permission')
    args = parser.parse_args()
    try:
        record = json.loads(args.file.read_text(encoding='utf-8'))
        schema(record)
        if args.fingerprint:
            print(fingerprint(record))
            return 0
        if args.review_fingerprint:
            print(review_fingerprint(record))
            return 0
        if args.selection_fingerprint:
            print(selection_fingerprint(record))
            return 0
        result = evaluate(record)
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({'record_valid': False, 'schema_error': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['record_valid'] else 1


if __name__ == '__main__':
    sys.exit(main())
