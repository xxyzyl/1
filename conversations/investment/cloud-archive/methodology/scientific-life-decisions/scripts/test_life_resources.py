#!/usr/bin/env python3
"""Synthetic behavioral tests for shared-resource accounting, not life outcomes."""
import copy
from decimal import Decimal
import json
import unittest

from check_life_resources import check, parse_record


def sample():
    return {'architecture': '4.0', 'snapshot_id': 'synthetic', 'revision': 1,
            'period': {'id': 'week-example', 'description': '合成单周增量时间预算', 'timezone': 'Etc/UTC'},
            'resources': [{'id': 'time', 'name': '时间', 'unit': '小时', 'capacity': 10,
                           'baseline': 0, 'reserve': 1, 'source': '合成题设'}],
            'actions': [
                {'id': 'family', 'description': '家庭承诺', 'owner_domain': 'D03', 'affected_domains': ['D09'], 'status': 'committed', 'demand': {'time': 2}},
                {'id': 'work', 'description': '项目备选', 'owner_domain': 'D04', 'affected_domains': ['D05'], 'status': 'proposed', 'demand': {'time': 5}},
                {'id': 'learn', 'description': '学习备选', 'owner_domain': 'D05', 'affected_domains': ['D04'], 'status': 'proposed', 'demand': {'time': 4}}],
            'scenarios': [{'id': 'both', 'action_ids': ['family', 'work', 'learn']},
                          {'id': 'work_only', 'action_ids': ['family', 'work']}]}


class ResourceTests(unittest.TestCase):
    def test_duplicate_json_fields_are_rejected(self):
        raw = json.dumps(sample())
        variants = [raw.replace('"baseline": 0', '"baseline": 11, "baseline": 0'),
                    raw[:-1] + ', "actions": []}']
        for text in variants:
            with self.assertRaisesRegex(ValueError, '重复JSON字段'):
                parse_record(text)

    def test_baseline_only_is_valid(self):
        r = sample()
        r['actions'] = []
        r['scenarios'] = [{'id': 'baseline', 'action_ids': []}]
        self.assertEqual(check(r)['scenarios'][0]['resources'][0]['remaining'], '9')

    def test_joint_conflict_and_alternatives(self):
        result = check(sample())['scenarios']
        self.assertEqual([s['status'] for s in result], ['资源冲突', '资源可行'])
        self.assertEqual(result[0]['resources'][0]['total_demand'], '12')

    def test_cross_domain_action_is_counted_once(self):
        r = sample()
        r['actions'][0]['affected_domains'] = ['D01', 'D02', 'D04', 'D09']
        self.assertEqual(check(r)['scenarios'][1]['resources'][0]['total_demand'], '8')

    def test_duplicate_action_rejected(self):
        r = sample()
        r['actions'].append(copy.deepcopy(r['actions'][0]))
        with self.assertRaises(ValueError):
            check(r)
        r = sample()
        r['scenarios'][0]['action_ids'].append('family')
        with self.assertRaises(ValueError):
            check(r)

    def test_cannot_drop_existing_commitment(self):
        r = sample()
        r['scenarios'][1]['action_ids'].remove('family')
        with self.assertRaises(ValueError):
            check(r)

    def test_unknown_does_not_become_zero(self):
        r = sample()
        r['actions'][2]['demand']['time'] = None
        result = check(r)['scenarios'][0]
        self.assertEqual(result['status'], '待补资源数据')
        self.assertIsNone(result['resources'][0]['total_demand'])

    def test_known_conflict_survives_unknown(self):
        r = sample()
        r['actions'][1]['demand']['time'] = 12
        r['actions'][2]['demand']['time'] = None
        self.assertEqual(check(r)['scenarios'][0]['status'], '资源冲突')

    def test_capacity_change_changes_fingerprint(self):
        r = sample()
        old = check(r)
        r['resources'][0]['capacity'] = 7
        new = check(r)
        self.assertNotEqual(old['input_fingerprint'], new['input_fingerprint'])
        self.assertEqual(new['scenarios'][1]['status'], '资源冲突')

    def test_numeric_validation(self):
        for invalid in (True, -1, Decimal('NaN'), Decimal('Infinity'), '10'):
            r = sample()
            r['resources'][0]['capacity'] = invalid
            with self.assertRaises(ValueError):
                check(r)

    def test_malformed_enum_is_rejected(self):
        for field in ('owner_domain', 'status'):
            for invalid in ([], {}):
                r = sample()
                r['actions'][0][field] = invalid
                with self.assertRaises(ValueError):
                    check(r)

    def test_exact_decimal_boundary(self):
        r = sample()
        r['resources'][0].update(capacity=Decimal('0.3'), reserve=0)
        r['actions'] = [r['actions'][0]]
        r['actions'][0]['demand']['time'] = Decimal('0.3')
        r['scenarios'] = [{'id': 'one', 'action_ids': ['family']}]
        self.assertEqual(check(r)['scenarios'][0]['resources'][0]['remaining'], '0')

    def test_each_resource_requires_explicit_demand(self):
        r = sample()
        r['resources'].append({'id': 'cash', 'name': '资金', 'unit': 'CNY', 'capacity': 100,
                               'baseline': 0, 'reserve': 0, 'source': '合成题设'})
        with self.assertRaises(ValueError):
            check(r)
        for a in r['actions']:
            a['demand']['cash'] = 0
        self.assertEqual(len(check(r)['scenarios'][0]['resources']), 2)


if __name__ == '__main__':
    unittest.main()
