# API_CONTRACT.md — API 合约草案

## 通用规则

- 路径前缀：`/api/v1`。
- 请求和响应使用 JSON。
- 金额、时长、概率等精确数值用字符串。
- 写接口支持 `Idempotency-Key` 请求头。
- 每个响应包含 `request_id`，错误响应包含 `code`、`message`、`details`。
- 后端根据服务端授权记录判断权限，前端传来的状态只作为用户输入。

## 错误格式

```json
{
  "request_id": "req_123",
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "所选方案超过每周可用时间。",
    "details": {"resource_type": "time", "over_by": "120"}
  }
}
```

资源冲突通常返回 200 或 409 取决于业务语义。若用户请求的是“检查方案”，返回 200 并在结果中标明冲突；若用户请求的是“创建执行计划且必须可执行”，可返回 409。

## 端点

### POST `/intake/messages`

接收用户输入，保存原文，抽取候选事实、目标、约束和决策问题。

请求：

```json
{
  "content": "我每周只有 8 小时，但想接单和学习。",
  "source_type": "user_message",
  "occurred_at": null
}
```

响应：

```json
{
  "message_id": "msg_1",
  "candidate_evidence": [],
  "candidate_goals": [],
  "candidate_decision_cases": []
}
```

### GET `/life/snapshot`

返回当前全局快照、未知项和需要用户确认的事实。

### POST `/decision-cases`

创建一次决策。

必填：`title`、`question`、`related_domain_codes`。可选：`goal_ids`、`constraint_ids`、`deadline`。

### POST `/decision-cases/{id}/run`

运行或继续八阶段引擎。请求中可指定 `target_stage`，也可让系统推进到下一可解释阶段。

响应应包含：当前阶段、建议状态、未知项、备选方案、资源核算摘要、反方复核结果和下一步建议。

### POST `/resource-checks`

对一个或多个方案进行资源核算。输入见 `examples/resources-over-budget.json`。

响应：

```json
{
  "status": "conflict",
  "resources": [
    {
      "resource_type": "time",
      "capacity": "600",
      "total_required": "720",
      "unit": "minute",
      "period": "week",
      "conflict": true
    }
  ]
}
```

### POST `/choices`

保存用户选择。保存后不得覆盖历史选择；用户改变主意时创建新 choice 版本。

### POST `/actions`

创建行动项。若行动会触达外部系统，必须有有效 authorization；否则只创建本地草稿。

### PATCH `/actions/{id}`

更新执行状态。允许状态：`not_started`、`in_progress`、`paused`、`completed`、`stopped`。

### POST `/feedback-events`

记录实际结果。反馈可以来自用户输入、外部数据源或系统观察，但必须保存来源。

### GET `/review-queue`

返回因条件变化、授权撤销、资源变化或反馈异常而需要复核的建议。

### POST `/authorizations`

创建或更新授权。授权必须包含数据源、可读范围、可写范围、用途、到期时间和撤销方式。

### DELETE `/authorizations/{id}`

撤销授权。撤销后，队列中依赖该授权且尚未执行的外部动作必须停止。

## 幂等

外部动作、创建行动、保存选择都要使用幂等键。重复请求应返回同一结果或明确提示已处理，不能产生重复外部效果。
