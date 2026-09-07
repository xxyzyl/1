# SPEC.md

## 1. 功能模块

### 1.1 用户与授权

支持用户建立目标、偏好、底线、可用资源和数据授权。授权应按数据源、字段、用途和有效期拆分，可撤回。

### 1.2 人生总控

维护有限的全局快照，而不是复制整个人生。根据当前问题选择相关领域和必要信息，分析跨领域影响，协调共同资源、优先级、承诺、风险和反馈周期。

### 1.3 九大领域

`D01` 健康恢复；`D02` 心理调节；`D03` 关系家庭；`D04` 职业劳动与价值创造；`D05` 学习能力与探索；`D06` 财务资产与保障；`D07` 居住日常与基础设施；`D08` 社群公共参与与生态责任；`D09` 休闲审美与生命体验。

领域模块负责记录状态、目标、项目、风险、承诺和结果，不负责孤立地优化自身。

### 1.4 决策引擎 S1—S8

S1 定义问题；S2 建立事实；S3 生成方案；S4 约束与比较；S5 反驳与复核；S6 建议与取舍；S7 授权执行；S8 反馈更新。每一步生成可追溯产物，并允许按缺口回退。

### 1.5 主动服务

在用户授权范围内读取日历、任务或文件导入数据；识别目标缺口、资源冲突、过期数据和异常变化；主动提出最少量补问；证据充分时生成建议；关键冲突必须交给用户确认。

### 1.6 项目与行动

将用户选择转为项目、任务、负责人、截止时间、预算、验收标准和停止条件。系统只在获得明确授权时执行外部动作。

### 1.7 反馈与复盘

记录预测、执行、实际结果、环境变化和判断误差。按日记录执行，按周期协调资源，待效果显现后评价项目；反馈应能回退到受影响的 S1—S8 阶段。

## 2. 用户流程

首发流程：用户输入“我想在职转型” → 系统询问目标、期限、可用时间、现有承诺和底线 → 生成有限快照 → 识别职业、学习、财务、健康和家庭影响 → 补充关键证据 → 生成含维持现状/小规模试行/暂缓的方案 → 先检查硬约束再比较 → 展示反对理由和反转条件 → 用户选择 → 创建试行项目 → 跟踪执行与反馈。

用户可以随时修正目标、撤回授权、标记数据错误或要求重新运行。系统不得因数据不足而强行给出确定答案。

## 3. 核心数据结构（设想）

```ts
type Evidence = { id: string; claim: string; source: string; sourceType: 'user'|'document'|'api'|'inference'; capturedAt: string; freshness?: string; confidence?: 'high'|'medium'|'low'|'unknown'; };
type Constraint = { id: string; label: string; kind: 'hard'|'soft'; value?: unknown; unit?: string; source: string; active: boolean; };
type Goal = { id: string; title: string; horizon?: string; priority?: number; status: 'active'|'paused'|'completed'|'unknown'; evidenceIds: string[]; };
type Resource = { id: string; kind: 'time'|'money'|'energy'|'attention'|'commitment'; amount?: number; unit?: string; period?: string; source: string; confidence: string; };
type Option = { id: string; title: string; requirements: Resource[]; impacts: string[]; risks: string[]; reversible: boolean; assumptions: string[]; };
type Decision = { id: string; stage: 'S1'|'S2'|'S3'|'S4'|'S5'|'S6'|'S7'|'S8'; goalIds: string[]; evidenceIds: string[]; optionIds: string[]; recommendation?: string; userDecision?: string; executionStatus: 'unknown'|'planned'|'in_progress'|'completed'|'stopped'; version: number; invalidatedBy?: string[]; };
type Action = { id: string; decisionId: string; title: string; dueAt?: string; budget?: Resource[]; acceptance?: string; stopConditions?: string[]; status: string; };
```

## 4. 接口设想

- `POST /api/v1/intakes` 创建问题与初始目标。
- `GET /api/v1/snapshots/:id` 获取与当前问题相关的有限快照。
- `POST /api/v1/decisions` 创建或推进决策运行。
- `POST /api/v1/decisions/:id/review` 进行反驳、复核和失效检查。
- `POST /api/v1/decisions/:id/choose` 保存用户选择，不等于执行。
- `POST /api/v1/actions` 创建行动计划。
- `POST /api/v1/feedback` 写入实际结果和复盘。
- `POST /api/v1/connectors/import` 导入日历、任务或文件数据。
- `GET /api/v1/notifications` 获取需要用户确认的缺口、冲突和提醒。

所有接口应返回 `traceId`、数据新鲜度、证据引用和状态字段。未来接入外部平台前，先提供 CSV/JSON 文件导入和人工确认。

