# 本地接手说明

将压缩包解压到固定目录，在本地 Codex 中打开 `life-management-codex`。若你已有代码仓库，先把本包放在独立目录供核对，不直接覆盖原仓库。根目录有当前`AGENTS.md`；`archive/`内旧同名文件是历史内容。

把下面整段发给本地 Codex：

> 这是“人生管理系统”的完整工程上下文包。请先读取根目录 README.md、AGENTS.md、CONTEXT.md、SPEC.md、ARCHITECTURE.md、TODO.md，以及 docs/ADR-001-engineering-baseline.md。检查已有代码和未提交修改，核对当前方法源码及 validation/VALIDATION_REPORT.md。简要说明你理解的产品目标、现有资产和下一步，然后直接推进 TODO.md 的 P0，不停在提出计划。复用现有确定性脚本，先建立可运行的服务骨架、持久化、版本化决策记录和资源冲突演示；保持建议、用户选择和执行状态独立。技术配置按当前ADR，缺少模型密钥时用明确标注的mock继续。先用合成数据，不接入账户，不修改全局Codex配置，不部署上线。每完成一个可运行切片，更新TODO、启动方式、实际测试结果和剩余问题；已有用户文件必须保留。

“本地 Codex”是开发助手，不是成品产品运行时。本包的`.env.example`是未来应用配置，不是Codex账号登录配置，也不是现有Python脚本必需配置。

现在可运行的只有 `README.md` 列出的脚本。后续本地 Codex 建立API/前端后，应新增真实可执行的启动命令、依赖锁文件、数据库迁移和演示方式，再把README的进度改为已实现。不要先运行不存在的`npm run dev`、`docker compose up`或未经核验的安装脚本。

如果只想继续用文件方式管理个人目标，可另行参考 `archive/legacy-v2/START_HERE.md`，并按 `docs/LEGACY_MIGRATION.md` 迁移到3.0状态与4.0领域规则。本次开发不需要先询问你的收入、健康或履历。
