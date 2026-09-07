# 迁移核验清单

核验日期：2026-09-07。

## 已取得的资料

- 五个对话的接口可读取文字，合计 207 个返回轮次；保留于 conversations/<代号>/history.md。它不是平台完整数据导出。
- 四个云端归档包已上传至同一 GitHub 仓库的 LFS 存储通道，再下载到本机，逐一验证大小和 SHA256。其解压文件位于各自 cloud-archive/，原始 ZIP 位于 archives/。
- 原始上下文包、PRD Word、设计 Markdown、PPT 和 SVG 本机已有文件保留于 reference/。

| 对话 | ZIP | SHA256 | 本机状态 |
|---|---|---|---|
| 主对话/技术 | technical-archive.zip | bd48f16f78d54bf7026f1c686d29d236077b6cb2e073f64e9c6208f1f65a3cfe | 已下载、哈希核验、解压 |
| 产品 | product-archive.zip | c725ce2d471aa9f2c14b0b619fd6cb262085bcd4680738d1c3c391110d87988f | 原始 ZIP 待接收；已有文字和部分原件 |
| 宣传 | promotion-archive-final.zip | 1aac6b8404d3b2b976c58c32c87039c5344a511b0252a2eda63c941fd87d002c | 已下载、哈希核验、解压 |
| 投资 | investment-archive.zip | d6f5417c5561577d22772215a870fad422e112cbc36678d15e995fdb54eafe3f | 已下载、哈希核验、解压 |
| 投资顾问 | investment-advisor-archive.zip | 77a7888396a53f56c138f88d868d342f0618f66d09de7cfe7f782264af474538 | 已下载、哈希核验、解压 |

## 完整性边界

四个 cloud-archive/ 中原始 manifest、history、missing-files 保留云端生成时的内容。其中“仓库为空”“尚未推送”是当时状态，并非本资料库的当前状态。

平台未提供的完整逐字消息、已经失效的早期附件、未能确认来源的图片不能凭空恢复。具体见各目录 missing-files.md。宣传归档中缺失的投资人路演 PPT 已在技术等其他来源中取得；本机 PRD Word 也单独补入 reference/local-originals/。

解压目录中的 Python 缓存和 *.openai-download-* 临时下载残片不纳入 Git；原始 ZIP 保持下载字节不变，可能仍包含云端打包时留下的缓存。不同来源同名或同内容文件保持各自位置，避免覆盖；这些重复文件不能当作不同成果数量。

临时上传授权仅用于迁移，不包含在此资料库中。
