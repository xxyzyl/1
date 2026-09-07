"""Synthetic workflow regressions; not a benchmark for real-life decision quality."""
import copy
import unittest

from decision_engine import evaluate, fingerprint, review_fingerprint, selection_fingerprint
from check_decision import validate


def example():
    record = {
        'protocol': '3.0', 'decision_id': 'synthetic-learning', 'revision': 1,
        'problem': {'question': '本周选择哪个学习计划？', 'goal': '完成一份汇总表', 'source': '合成任务题设',
                    'constraints': [{'id': 'C1', 'description': '最多4小时', 'source': '合成题设'}]},
        'evidence': [{'id': 'E1', 'source': '合成题设：A需8小时，B需3小时', 'date': '未知', 'checked_at': '2026-09-05', 'status': '用户陈述', 'decisive': True}],
        'options': [
            {'id': 'A', 'description': '8小时课程，需8>4小时', 'constraint_checks': {'C1': '不满足'}},
            {'id': 'B', 'description': '3小时课程，可留1小时机动', 'constraint_checks': {'C1': '满足'}}],
        'gaps': [],
        'comparison': {'revision': 1, 'input_fingerprint': '', 'method': '硬约束筛选与可行方案比较',
                       'artifact': 'A:8>4；B:3<=4，留1小时；只讨论本周时间可行性',
                       'option_ids': ['A', 'B'], 'evidence_ids': ['E1'],
                       'strongest_objection': '满足时间约束不保证学习效果',
                       'reversal_conditions': ['若实际可用时间不足3小时，B也不满足约束'], 'conditions': []},
        'review': {'revision': 1, 'input_fingerprint': '', 'completed': True, 'mode': '主智能体自审', 'artifact': '已复算8>4与3<=4，仅核对合成题设'},
        'recommendation': {'status': '建议可供选择', 'option_ids': ['B']},
        'user_choice': {'status': '未决定', 'option_ids': [], 'source': ''},
        'execution': {'status': '未开始', 'authorization_source': '', 'action_record': ''},
    }
    bind(record)
    return record


def bind(record):
    for section in ('comparison', 'review'):
        record[section]['revision'] = record['revision']
        record[section]['input_fingerprint'] = fingerprint(record)
    record['review']['target_fingerprint'] = review_fingerprint(record)


def markdown(record):
    headings = ['1. 问题、目标与约束', '2. 本次使用的方法', '3. 证据、假设与未知', '4. 方案与取舍',
                '5. 反对理由与敏感性', '6. 建议、条件与下一步', '7. 复核与证据缺口', '8. 结果跟踪']
    body = ['合成题设，4小时资源。', 'M01检查题设；M05筛可行方案；M23保留用户选择。',
            '来源：合成题设E1\n日期：2026-09-05', 'A超时；B可行。', '用时估计变化可能改变可行性。',
            '建议B，只针对时间约束。', '复核方式：实际复算题设数值', '复盘触发条件：本周课程完成时']
    text = f"协议版本：3.0\n记录编号：{record['decision_id']}\n记录类型：合成示例\n输入版本：{record['revision']}\n建议状态：{record['recommendation']['status']}\n用户选择：{record['user_choice']['status']}\n执行状态：{record['execution']['status']}\n状态记录：state.json\n阻断性缺口：无\n"
    return text + '\n'.join(f'\n## {h}\n\n{b}\n' for h, b in zip(headings, body))


class EngineRegression(unittest.TestCase):
    def test_rejected_alternative_does_not_block_feasible_choice(self):
        result = evaluate(example())
        self.assertTrue(result['record_valid'])
        self.assertEqual(result['feasible_option_ids'], ['B'])
        self.assertEqual(result['next_stage'], 'S6')

    def test_score_cannot_override_time_constraint(self):
        r = example(); r['recommendation']['option_ids'] = ['A']
        r['comparison']['artifact'] += '；但A评分95、B75。'
        result = evaluate(r)
        self.assertEqual(result['supported_recommendation_status'], '待补证')
        self.assertFalse(result['record_valid'])

    def test_old_choice_does_not_authorize_or_improve_new_advice(self):
        r = example(); r['user_choice'] = {'status': '已决定', 'option_ids': ['A'], 'source': '合成用户昨日选择'}
        r['user_choice'].update(revision=1, selection_fingerprint=selection_fingerprint(r))
        result = evaluate(r)
        self.assertEqual(result['supported_recommendation_status'], '建议可供选择')
        self.assertEqual(result['execution_status'], '未开始')
        self.assertTrue(result['execution_issues'])
        self.assertEqual(result['next_stage'], 'S6')

    def test_changed_input_cannot_reuse_review_even_without_revision_bump(self):
        r = example(); r['problem']['goal'] = '改为两份汇总表'
        result = evaluate(r)
        self.assertFalse(result['record_valid'])
        self.assertTrue(any(x['stage'] == 'S5' for x in result['blocking_issues']))

    def test_version_bump_invalidates_both_artifacts(self):
        r = example(); r['revision'] = 2
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')

    def test_rewritten_comparison_cannot_reuse_prior_review(self):
        r = example(); r['comparison']['artifact'] = '改用新的比较结果'
        result = evaluate(r)
        self.assertEqual(result['supported_recommendation_status'], '待补证')
        self.assertTrue(any(x['stage'] == 'S5' for x in result['blocking_issues']))

    def test_different_feasible_recommendation_requires_review(self):
        r = example()
        r['options'].append({'id': 'C', 'description': '另一份3小时方案', 'constraint_checks': {'C1': '满足'}})
        r['comparison']['option_ids'].append('C'); bind(r)
        r['recommendation']['option_ids'] = ['C']
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')

    def test_unknown_hard_constraint_blocks_recommended_option(self):
        r = example(); r['options'][1]['constraint_checks']['C1'] = '未知'; bind(r)
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')

    def test_unverified_key_premise_only_supports_explicit_condition(self):
        r = example(); r['evidence'][0]['status'] = '待核实'; bind(r)
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')
        r['comparison']['conditions'] = ['B总耗时确实不超过4小时']; r['recommendation']['status'] = '条件建议'
        bind(r)
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '条件建议')
        self.assertTrue(evaluate(r)['record_valid'])

    def test_honest_pending_record_is_valid_but_not_ready(self):
        r = example(); r['review']['completed'] = False; r['recommendation']['status'] = '待补证'
        result = evaluate(r)
        self.assertTrue(result['record_valid'])
        self.assertEqual(result['supported_recommendation_status'], '待补证')

    def test_subagent_review_needs_actual_task_reference(self):
        r = example(); r['review']['mode'] = '子智能体复核'
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')

    def test_decisive_evidence_cannot_be_omitted_from_comparison(self):
        r = example()
        r['evidence'].append({'id': 'E2', 'source': '合成题设：B可能增加练习时间', 'date': '未知', 'checked_at': '未知', 'status': '待核实', 'decisive': True})
        bind(r)
        result = evaluate(r)
        self.assertEqual(result['supported_recommendation_status'], '待补证')
        self.assertTrue(any('E2' in x['reason'] for x in result['blocking_issues']))

    def test_execution_claim_needs_authorization_reference(self):
        r = example(); r['execution'].update(status='执行中', action_record='合成题设：开始练习')
        self.assertFalse(evaluate(r)['record_valid'])

    def test_placeholder_sources_and_review_identity_do_not_count(self):
        for key in ('source', 'checked_at'):
            r = example(); r['evidence'][0]['status'] = '已核实'; r['evidence'][0][key] = '待确认'; bind(r)
            self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')
        r = example(); r['review'].update(mode='子智能体复核', task_id='未知')
        self.assertEqual(evaluate(r)['supported_recommendation_status'], '待补证')

    def test_changed_selected_content_does_not_inherit_old_choice(self):
        r = example(); r['user_choice'] = {'status': '已决定', 'option_ids': ['B'], 'source': '合成用户选择B', 'revision': 1}
        r['user_choice']['selection_fingerprint'] = selection_fingerprint(r)
        self.assertEqual(evaluate(r)['next_stage'], 'S7')
        r['revision'] = 2; r['options'][1]['description'] += '；新增另一项承诺'; bind(r)
        result = evaluate(r)
        self.assertEqual(result['supported_recommendation_status'], '建议可供选择')
        self.assertTrue(result['execution_issues'])
        self.assertEqual(result['next_stage'], 'S6')

    def test_no_execution_record_does_not_imply_not_started(self):
        r = example(); r['execution']['status'] = '未知'; r['user_choice']['status'] = '未知'
        result = evaluate(r)
        self.assertTrue(result['record_valid'])
        self.assertEqual(result['execution_status'], '未知')
        self.assertEqual(result['user_choice'], '未知')

    def test_missing_option_and_duplicate_ids_rejected(self):
        r = example(); r['recommendation']['option_ids'] = ['C']
        with self.assertRaises(ValueError): evaluate(r)
        r = example(); r['options'].append(copy.deepcopy(r['options'][0]))
        with self.assertRaises(ValueError): evaluate(r)

    def test_markdown_must_match_structured_record(self):
        r = example(); text = markdown(r)
        self.assertEqual(validate(text, r), [])
        self.assertTrue(validate(text.replace('用户选择：未决定', '用户选择：已决定'), r))
        self.assertTrue(validate(text))

    def test_legacy_v2_record_still_reads_without_state(self):
        text = markdown(example()).replace('协议版本：3.0', '协议版本：2.0').replace('建议状态：建议可供选择', '建议状态：已决定')
        self.assertEqual(validate(text), [])
        self.assertTrue(validate(text.replace('来源：合成题设E1', '来源：')))


if __name__ == '__main__':
    unittest.main()
