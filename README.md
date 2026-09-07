# 人生管理系统：协作资料库

此目录用于本地阅读、修改、分享和 GitHub 协作。它收集已实际取得的项目成果，并保留五个云端对话的来源。

当前已取得“主对话/技术”“宣传”“投资”“投资顾问”四份完整归档，以及五个对话的可读取历史文字和本机已有成果。“产品”归档正在逐文件核对补齐。历史附件是否可恢复，以 [迁移清单](MIGRATION_STATUS.md) 为准。本资料库包含项目源材料，不代表应用已完成部署。

## 从哪里开始

- [工程上下文说明](reference/product-context/README.md)：产品定位与需求。
- [需求说明](reference/product-context/SPEC.md)、[架构说明](reference/product-context/ARCHITECTURE.md)、[待办](reference/product-context/TODO.md)。
- [本机已有成果](reference/local-originals/)：PPTX、SVG、设计 Markdown、PRD Word 和原始上下文 ZIP。
- [五个对话的文字备份](conversations/)：按来源分别保存，保留读取范围说明。
- [主对话/技术成果](conversations/technical/cloud-archive/)：设计原件与工程骨架。
- [技术工程接手入口](conversations/technical/cloud-archive/docs/工程上下文包/life-management/START_HERE.md)。
- [投资成果与方法源码](conversations/investment/cloud-archive/START_HERE.md)。
- [宣传成果](conversations/promotion/cloud-archive/)：图片、PPT、脑图及源文件。
- [投资顾问成果](conversations/investment-advisor/cloud-archive/)。
- [原始归档 ZIP](archives/)：保留云端交付原件；文件夹内 cloud-archive 为解压后的可编辑版本。
- [远程协作说明](COLLABORATION.md)。

仓库：https://github.com/xxyzyl/1

PPTX 用 PowerPoint 打开并编辑；DOCX 用 Word 打开；SVG 用浏览器查看，使用矢量编辑器可编辑；Markdown 可直接编辑。

## 同步与分享

完整 Git 下载副本可在本目录执行 `git pull --ff-only` 获取最新版本。执行前先处理自己的未提交修改。ZIP 下载副本不包含 Git 历史。

Windows 用户可双击 `更新本地.cmd` 拉取 GitHub 更新，或双击 `打开GitHub仓库.url` 打开远程项目。

与他人分享仓库地址或 ZIP 即可供其阅读。远程修改建议由对方 Fork 后创建独立分支并提交 Pull Request，由仓库所有者审查合并。

本仓库保持各对话原始版本，归档中的旧说明不代表当前完成状态。以 MIGRATION_STATUS.md 的核验记录为准。
