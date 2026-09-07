# 系统需求说明

## 1. 用户与首个场景

首个目标用户是假设中的在职职业转型者：有本职工作和家庭承诺，希望在 8–12 周形成可展示作品并开始求职。系统必须允许用户选择“不开始、缩小、延期或暂缓”。

## 2. 功能模块

### 2.1 用户与授权
注册、登录、时区、目标偏好、数据来源列表、连接/断开、导出/删除。每个来源记录 scope、状态、最后同步时间和撤销时间。

### 2.2 目标与约束
目标、阶段、期限、不可牺牲底线、可调约束、已有承诺、观察窗口。目标变更必须产生版本。

### 2.3 全局快照与资源账
保存相关领域状态、时间预算、现金预算、固定基线、行动需求、缓冲、单位和周期。基线 + 唯一行动需求 + 缓冲 ≤ 总量；互斥方案分别核算。

### 2.4 决策引擎
实现 S1–S8。输出真实备选、计算结果、最大未知、反对理由、反转条件、用户选择和执行状态。

### 2.5 计划与执行
把用户选择转为行动、负责人、开始/截止、验收条件、依赖、暂停和停止原因。支持条件变化后的重排，但不能悄悄改变用户承诺。

### 2.6 反馈与复盘
记录预期、实际投入、成果、环境变化和解释；区分日常行动、周期协调、项目评价和方向复盘。

### 2.7 AI 编排
将自然语言转为结构化草稿；检索授权来源；提出最少补问；生成方案解释。所有 AI 事实必须带来源或标记为推断/假设。

### 2.8 试点与商业验证
记录试点付款、退款、复盘完成、续费、人均人工分钟、模型/云直接成本和对照方案结果。不得把门槛写成行业基准。

## 3. 用户流程

1. 用户输入目标、期限和可用时间。
2. 系统识别涉及领域，显示缺失信息，只追问最能改变选择的一项。
3. 系统建立带版本的全局快照并检查资源冲突。
4. 系统生成保留、缩减、延期、替换和不行动等真实方案。
5. 用户查看差异、代价和条件并作选择。
6. 系统生成行动计划和验收方式。
7. 用户或连接器提交变化；系统显示受影响事项和重新计算结果。
8. 用户确认是否更新；到观察窗口后记录实际结果和下一轮建议。

## 4. 核心数据结构

```text
User(id, timezone, locale, created_at)
Goal(id, user_id, title, description, horizon, status, version, constraints[])
DomainState(id, user_id, domain_code, statement, metric_json, source_refs[], observed_at, confidence)
Commitment(id, user_id, title, domain_code, time_window, minutes, cost_minor, currency, fixed)
ResourceSnapshot(id, user_id, revision, period_start, period_end, time_budget, money_budget, buffer, commitments[], source_refs[])
Decision(id, user_id, stage, input_revision, question, options[], recommendation_status, user_choice, execution_status)
Option(id, decision_id, title, resource_requirements[], tradeoffs[], exit_condition)
Action(id, decision_id, title, owner, start_at, due_at, acceptance, status, global_action_id)
Evidence(id, entity_type, entity_id, claim, kind, source_uri, accessed_at, excerpt, applicability)
Feedback(id, action_id, expected, actual, outcome, cause_hypotheses[], observed_at)
Connection(id, user_id, provider, scopes[], status, last_sync_at, revoked_at)
TrialEvent(id, cohort_id, user_id, event_type, amount_minor, currency, minutes, occurred_at)
```

## 5. API 设想

`POST /v1/goals`、`GET /v1/snapshots/current`、`POST /v1/decisions/preview`、`POST /v1/decisions/{id}/choose`、`POST /v1/actions`、`POST /v1/feedback`、`POST /v1/connections/{provider}/authorize`、`DELETE /v1/connections/{id}`、`GET /v1/audit-events`。

关键接口必须返回 `input_revision`、`recommendation_status`、`user_choice`、`execution_status`、`evidence_refs`、`unknowns` 和 `reversal_conditions`。写操作使用幂等键；连接器同步需分页、限速和增量游标。

## 6. 验收指标

纵向切片能够处理 10 小时容量下的学习/作品/求职/家庭/缓冲案例；输入从 10 小时变为 8 小时后，能指出受影响任务并重新计算；用户选择前不改变承诺；所有情景计算可复算；删除连接后不再读取；页面清楚显示模拟/待验证边界。
