# 系统需求说明

## 1. 用户与基本概念

系统服务于单个用户，也为未来多用户扩展保留租户边界。核心对象包括：用户、价值与底线、人生领域、目标、项目、行动、数据源、数据记录、决策、证据、建议、授权、反馈、复盘和通知。

## 2. 功能模块

| 模块 | 需求 | 第一版状态 |
|---|---|---|
| 总控 | 汇总状态、目标、资源、承诺和领域影响 | 文件协议已完成 |
| 领域管理 | 管理9个领域及领域专属指标、项目和约束 | 数据结构已完成 |
| 决策引擎 | 按八阶段形成证据链和可逆试行方案 | 协议与模板已完成 |
| 主动采集 | 拉取授权数据源的新增和变化 | 未实现 |
| 主动补问 | 计算信息价值，只问关键缺口 | 规则已设计，未产品化 |
| 建议中心 | 输出依据、代价、风险、条件和选项 | 规则与示例已完成 |
| 执行跟踪 | 任务、验收标准、停止条件和观察窗口 | 文件记录已完成 |
| 反馈复盘 | 对照预测与结果，更新状态和策略 | 规则已完成 |
| 数据治理 | 授权、来源、脱敏、审计、删除和导出 | 需求已提出 |
| 通知 | 关键缺口、冲突、到期和复盘提醒 | 未实现 |

## 3. 用户流程

首次启用：用户提供未来三个月或一年最重要目标、价值偏好、不可牺牲底线、时间和资金范围、重要责任及正在使用的数据工具；系统读取现有项目文件，生成待确认的个人基线。

日常运行：系统同步授权来源→标准化和去重→更新领域状态→检查资源冲突和目标偏差→判断是否需要补问→生成建议或“无需调整”结论→记录用户选择→跟踪行动结果。

重要决策：用户提出问题→系统识别涉及领域→按八阶段运行→调用相关能力模块→形成备选和复核结果→用户选择是否采纳→系统仅执行已授权动作→在观察窗口后反馈更新。

## 4. 最小数据结构

```text
User(id, timezone, locale, created_at)
Value(id, user_id, statement, priority, source, updated_at)
Area(id, user_id, code, name, status, notes)
Goal(id, area_ids, title, desired_state, deadline, priority, status, evidence_rule)
Project(id, goal_id, title, budget_time, budget_money, commitments, status)
Action(id, project_id, title, owner, due_at, estimate, acceptance, stop_condition, status)
Source(id, user_id, type, provider, scopes, consent_status, last_sync_at)
Observation(id, source_id, area_id, kind, value, unit, observed_at, confidence, raw_ref)
Decision(id, question, goal_ids, constraints, stage, version, status, created_at)
Evidence(id, decision_id, claim, source_ref, evidence_level, collected_at, limitations)
Recommendation(id, decision_id, option, rationale, cost, risk, conditions, status)
Feedback(id, action_id, expected, actual, window, cause_class, updated_at)
AuditEvent(id, actor, action, object_type, object_id, timestamp, metadata)
```

## 5. 非功能需求

隐私最小化、可撤销授权、可导出和可删除；所有同步和建议可追溯；失败可重试且不重复写入；同一来源记录支持幂等；系统应支持离线文件模式；建议生成不能阻塞用户查看原始数据；重要操作有审计记录。

## 6. 接口设想

```text
POST /v1/intake                 接收用户文字、语音转写或文件索引
GET  /v1/state                  获取总控快照和领域状态
POST /v1/sync/{source_id}       同步指定数据源的变化
POST /v1/decisions              创建决策并启动八阶段流程
GET  /v1/decisions/{id}         查看证据、方案、建议和版本
POST /v1/recommendations/{id}/choice 记录用户采纳、拒绝或暂缓
POST /v1/actions/{id}/feedback  提交结果和主观体验
POST /v1/questions/answer       回答系统主动补问
GET  /v1/audit                  查询授权、同步和修改记录
```

