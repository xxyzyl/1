# 协作说明

## 本地继续工作

克隆仓库后，从 README.md 和 MIGRATION_STATUS.md 开始，确定已取得和待补齐的资料，再阅读 reference/product-context/ 的需求、架构和待办。

```sh
git clone https://github.com/xxyzyl/1.git life-management-system
cd life-management-system
git switch -c codex/your-task
```

修改后用 `git status`、`git diff` 检查，仅提交本次工作的文件，再推送自己的分支。

```sh
git add <本次修改的文件>
git commit -m "说明本次修改"
git push -u origin codex/your-task
```

没有仓库写权限的协作者先 Fork，向自己的仓库推送，再向本仓库提 Pull Request。

## 多对话归档

| 云端对话 | 专属目录 | 专属分支 |
|---|---|---|
| 主对话/技术 | conversations/technical/ | chat/technical |
| 产品 | conversations/product/ | chat/product |
| 宣传 | conversations/promotion/ | chat/promotion |
| 投资 | conversations/investment/ | chat/investment |
| 投资顾问 | conversations/investment-advisor/ | chat/investment-advisor |

不同对话从同一个 main 基点建立各自分支，只提交各自目录。项目汇总者按顺序审查并合并。历史备份保留不覆盖；新导入的 history.md 使用独立文件名或时间戳区分。

## 与 AI 工具协作

把仓库连接到具备 Git 写权限的执行环境，或让工具在本地克隆目录内工作。仅在网页聊天中提到仓库地址不代表已建立读写连接。

可使用以下工作指令：

> 阅读本仓库 README.md、MIGRATION_STATUS.md 和 reference/product-context/ 内的需求与架构资料，在独立分支完成本次明确指定的任务。保留原始成果和各对话目录，提交前展示实际修改，报告验证结果与未完成内容。
