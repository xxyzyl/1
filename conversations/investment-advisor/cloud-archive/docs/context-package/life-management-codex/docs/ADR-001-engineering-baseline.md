# ADR-001 — 工程基线统一

## 状态

已采纳，作为本包交给本地 Codex 的默认工程基线。

## 背景

历史上下文中出现过多套实现建议：SQLite 与 PostgreSQL、不同 API 端口、不同前端目录、不同环境变量命名。这些文档都保留在 `archive/` 中，但后续开发需要一个明确起点。

## 决定

- 后端采用 Python 3.12 + FastAPI。
- 前端采用 TypeScript + React。
- 主数据库采用 PostgreSQL。
- 前端端口 3000，后端端口 8000。
- MVP 默认使用 mock 模型适配器。
- 外部连接器默认关闭。
- Redis 和对象存储作为后续扩展，不作为 P0 必需项。

## 理由

现有方法脚本已经是 Python，先用 FastAPI 可以最大限度复用资源核算和决策状态逻辑。PostgreSQL 支持事务、JSONB、审计记录和后续多用户隔离，比 SQLite 更适合作为商业化产品基线。mock 模型让本地 Codex 可以在没有真实密钥的情况下完成开发和测试。

## 影响

历史包中的旧端口、旧环境变量和旧数据库方案不删除，但只作为参考。新代码、测试和文档应以根目录 `README.md`、`SPEC.md`、`ARCHITECTURE.md`、`.env.example` 为准。
