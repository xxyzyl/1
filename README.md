# 人生管理系统：协作资料库

此目录用于本地阅读、修改、分享和 GitHub 协作。它收集已实际取得的项目成果，并保留五个云端对话的来源。

当前是迁移中的资料快照，尚不是云端项目的完整镜像，也不是已部署的可运行应用。云端已打包但尚未下载的文件见 [迁移清单](MIGRATION_STATUS.md)。

## 从哪里开始

- [工程上下文说明](reference/product-context/README.md)：产品定位与需求。
- [需求说明](reference/product-context/SPEC.md)、[架构说明](reference/product-context/ARCHITECTURE.md)、[待办](reference/product-context/TODO.md)。
- [本机已有成果](reference/local-originals/)：PPTX、SVG、设计 Markdown、PRD Word 和原始上下文 ZIP。
- [五个对话的文字备份](conversations/)：按来源分别保存，保留读取范围说明。
- [远程协作说明](COLLABORATION.md)。

仓库：https://github.com/xxyzyl/1

PPTX 用 PowerPoint 打开并编辑；DOCX 用 Word 打开；SVG 用浏览器查看，使用矢量编辑器可编辑；Markdown 可直接编辑。

## 同步与分享

完整 Git 下载副本可在本目录执行 `git pull --ff-only` 获取最新版本。执行前先处理自己的未提交修改。ZIP 下载副本不包含 Git 历史。

与他人分享仓库地址或 ZIP 即可供其阅读。远程修改建议由对方 Fork 后创建独立分支并提交 Pull Request，由仓库所有者审查合并。

本仓库保持各对话原始版本，归档中的旧说明不代表当前完成状态。以 MIGRATION_STATUS.md 的核验记录为准。
