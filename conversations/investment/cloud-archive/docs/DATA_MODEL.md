# DATA_MODEL.md — 数据模型草案

## 设计原则

数据模型要保存“当时为什么这样建议”，而不是只保存最终计划。每条事实、建议、选择、行动和结果都带来源、版本和时间。用户纠正信息时，不直接覆盖历史结论，而是生成新版本并触发复核。

## 核心表

| 表 | 关键字段 | 说明 |
|---|---|---|
| users | id, display_name, timezone, created_at | MVP 可单用户，但表结构从多用户开始 |
| user_profiles | user_id, preferences_json, privacy_json, updated_at | 保存偏好和隐私设置摘要 |
| life_snapshots | id, user_id, version, valid_from, summary_json | 某时点全局状态快照 |
| domains | code, name, description | D01-D09 固定字典 |
| domain_states | snapshot_id, domain_code, state_json, confidence | 每个领域的状态 |
| goals | id, user_id, domain_code, title, priority, status, horizon | 阶段目标和长期目标 |
| constraints | id, user_id, type, scope, value_json, hardness, source_id | 硬约束或软约束 |
| evidence_items | id, user_id, content, source_type, source_ref, occurred_at, acquired_at, confidence | 事实证据 |
| decision_cases | id, user_id, title, stage, recommendation_status, choice_status, execution_status, validity_status | 一次决策 |
| options | id, decision_case_id, title, actions_json, expected_benefits_json, risks_json | 备选方案 |
| resource_checks | id, decision_case_id, option_id, resource_type, result_json, status | 资源核算结果 |
| choices | id, decision_case_id, option_id, chosen_by_user, chosen_at, rationale | 用户选择记录 |
| action_items | id, user_id, decision_case_id, title, status, due_at, idempotency_key | 行动项 |
| feedback_events | id, user_id, action_id, decision_case_id, observed_at, content, outcome_json | 实际结果和观察 |
| authorizations | id, user_id, source, scope_json, operation_type, status, expires_at | 授权范围 |
| outbox_events | id, user_id, action_type, payload_json, idempotency_key, status | 外部执行队列 |
| audit_events | id, user_id, actor_type, event_type, entity_type, entity_id, occurred_at, metadata_json | 审计记录 |
| recommendation_dependencies | recommendation_id, entity_type, entity_id, entity_version | 建议依赖哪些事实或状态 |
| review_queue | id, user_id, entity_type, entity_id, reason, priority, status | 需要复核的项目 |

## 状态字段

`decision_cases` 至少保存四类状态：

| 字段 | 值 |
|---|---|
| recommendation_status | needs_evidence, conditional, ready_for_choice |
| choice_status | unknown, undecided, decided, deferred |
| execution_status | unknown, not_started, in_progress, paused, completed, stopped |
| validity_status | current, stale, superseded, archived |

## 资源数值

资源数值建议保存为字符串形式的 decimal，例如 `"2.50"`，并带单位和周期：

```json
{
  "resource_type": "time",
  "amount": "120",
  "unit": "minute",
  "period": "week"
}
```

API 层进入核心规则时转成 Decimal。禁止用二进制浮点直接参与资源核算。

## 来源时间

`occurred_at` 表示事情实际发生的时间，`acquired_at` 表示系统获得这条信息的时间。两者不能混用。用户转述过去事件时，`occurred_at` 可为空或模糊，`acquired_at` 必须存在。

## 纠正与删除

用户纠正事实时，保留原 evidence_item，创建 correction 关系和新 evidence_item。用户请求删除个人数据时，后续产品需要提供删除或匿名化策略；MVP 至少不能把已撤销授权的数据继续用于新建议。
