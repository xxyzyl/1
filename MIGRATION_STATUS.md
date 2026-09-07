# 迁移核验清单

核验日期：2026-09-07。

## 迁移结果

- 五个对话的当前可获取成果已落到本机，并纳入同一 Git 仓库。原始版本按来源隔离，便于查看与编辑。
- conversations/<代号>/history.md 为应用接口分页取得的文字备份，合计 207 个返回轮次；cloud-archive/history.md 为各云端对话提供的历史整理。两者保留，不相互覆盖；均不是平台完整原始数据导出。
- 主对话/技术、宣传、投资、投资顾问：四份 ZIP 经 GitHub 文件传输通道下载，逐一校验大小和 SHA256，再解压。原始 ZIP 字节保持不变。
- 产品：原始 ZIP 未能直接传输；依据云端 ZIP 的完整条目清单，复用其他归档中相同哈希的原件，并取得三个归档说明文件的准确文本，重建了全部 16 个文件。每个文件的大小与 SHA256 都与原清单一致。重新压缩为 product-archive-reconstructed.zip，ZIP 容器本身与云端原 ZIP 的哈希不同，不冒充原始压缩包。

| 对话 | 本地目录 | 已核验文件数 | 包类型 |
|---|---|---:|---|
| 主对话/技术 | conversations/technical/cloud-archive/ | 122 | 原始 ZIP |
| 产品 | conversations/product/cloud-archive/ | 16 | 文件一致的重建 ZIP |
| 宣传 | conversations/promotion/cloud-archive/ | 46 | 原始 ZIP |
| 投资 | conversations/investment/cloud-archive/ | 267 | 原始 ZIP |
| 投资顾问 | conversations/investment-advisor/cloud-archive/ | 271 | 原始 ZIP |

上述计数是接收或重建的归档内文件数，包含重复成果；不代表不同成果数量。最终 Git 跟踪文件数不含被忽略的缓存。

原始上下文包、PRD Word、设计 Markdown、PPT 和 SVG 本机已有文件保留于 reference/。各包 SHA256 和产品的逐文件核验表见 ARCHIVE_RECEIPTS.json。

## 历史资料边界

每个 cloud-archive/ 中原始 manifest、history、missing-files 保留云端生成时的内容。其中“仓库为空”“尚未推送”是当时状态，并非本资料库的当前状态。

平台未提供的完整逐字消息、已失效的早期附件、未能确认来源的图片不能凭空恢复。具体见各目录 missing-files.md。部分跨对话缺失项已由其他来源补齐：例如宣传归档中的投资人路演 PPT 已在技术等来源中取得；本机 PRD Word 也单独补入 reference/local-originals/。无法恢复的文件不会用截图或重生成版本冒充。

解压目录中的 Python 缓存和 *.openai-download-* 临时下载残片不纳入 Git；原始 ZIP 保持下载字节不变，可能仍包含云端打包时留下的缓存。不同来源同名文件保持各自位置。

临时上传授权不包含在本资料库中。
