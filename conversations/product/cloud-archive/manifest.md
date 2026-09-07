# 归档清单

生成时间：2026-09-07

| 路径 | 用途 | 来源 | 大小 | SHA256 |
|---|---|---|---:|---|
| `conversations/product/history.md` | 对话历史范围、需求、成果和限制 | 本次可见对话与项目历史摘要 | 4131 bytes | `1e7cf49029aed3038389364e8cdc51e0edca555fdf1de9747da7815057414f0c` |
| `conversations/product/manifest.md` | 文件清单与校验信息 | 本次归档 | 约 4000 bytes | 自身哈希不列入，避免自引用 |
| `conversations/product/missing-files.md` | 已知但当前无法取得的附件清单 | Library 检索和当前上下文 | 1557 bytes | `181740e7b9c2b4e816e3ab46b936fd165e906192f406628ab79f0e2a076e0fbe` |
| `conversations/product/slides/人生管理系统-投资人路演.pptx` | 投资人路演原始成果 | Library 原始文件，2026-09-06 | 115505 bytes | `46370625e721287dc69792a7f14d8dd0944bc1b4ae80e0260a2836b0a769ae37` |
| `conversations/product/slides/人生管理系统4.0-完整设计与模块详解.pptx` | 4.0 系统设计原始成果 | 本地已有原始文件 | 418777 bytes | `d413cd0c7c6d98d37a6301e0ae59718cb116784a944c77c4bb60be825ed54638` |
| `conversations/product/slides/人生管理系统4.0-完整设计与模块详解(1).pptx` | 4.0 系统设计同名近似版本，保留原文件名 | Library 原始文件，2026-09-07 | 418777 bytes | `d413cd0c7c6d98d37a6301e0ae59718cb116784a944c77c4bb60be825ed54638` |
| `conversations/product/docs/人生管理系统-本地Codex工程上下文包.zip` | 已有工程上下文包原件 | Library 原始文件，2026-09-07 | 376166 bytes | `6bad449321b736b693b6c66379a83f409d303e469f4f66c59486fc3a9ba742e2` |
| `conversations/product/docs/上下文包展开/` | 上下文包展开内容，便于本地 Codex 直接阅读 | 上述 ZIP 原件展开 | 见文件 | 见校验表 |
| `conversations/product/assets/` | 图片、SVG、截图预留目录 | 本次归档 | 空目录 | — |
| `conversations/product/src/` | 本对话专属代码预留目录 | 本次归档 | 空目录 | — |

## 上下文包展开文件校验

| 路径 | 大小 | SHA256 |
|---|---:|---|
| `conversations/product/docs/上下文包展开/.env.example` | 1012 | `9321f29708b345024c65f22722ea0747ea7eb49278ae975d40fbb187334f0955` |
| `conversations/product/docs/上下文包展开/AGENTS.md` | 3444 | `f3a892d94c99afea4332d6fe8f660c21dfcf836da2a9a29f917b3c64529ffe75` |
| `conversations/product/docs/上下文包展开/ARCHITECTURE.md` | 3312 | `add98917509048af4b501ca90cf3a07b38314525bc2dba5d03c796f01c93e3c6` |
| `conversations/product/docs/上下文包展开/CONTEXT_PACKAGE_MANIFEST.md` | 822 | `ce4b4afc5318fc40ccea902b24b35f66d554096c2868c3ba8d1302139f45f64d` |
| `conversations/product/docs/上下文包展开/README.md` | 4618 | `5cb93a863f738e4d5072d4438bcad5bbd6e10fc020fcf6723875cd9874c54932` |
| `conversations/product/docs/上下文包展开/SPEC.md` | 4860 | `e13e47afaab6a6c121c71f7ad763256e0fbec656cb27f99bd9cff8a776b8bf34` |
| `conversations/product/docs/上下文包展开/TODO.md` | 2192 | `d869692c596143728fb765df021787b2255abe944cdc6fa31edfaa8dbd58c75c` |
| `conversations/product/docs/上下文包展开/docs/CONTEXT.md` | 3825 | `12952249c87a47ed394209e4a35bdb6e8e6453a4aec4e2715653f7450414fe58` |
| `conversations/product/docs/上下文包展开/人生管理系统4.0-完整设计与模块详解.pptx` | 418777 | `d413cd0c7c6d98d37a6301e0ae59718cb116784a944c77c4bb60be825ed54638` |

## 校验说明

归档生成后，使用 `find` 逐文件计算大小和 SHA256，并使用 `unzip -t` 检查 ZIP。上下文包展开文件的逐项哈希已由最终校验命令计算；三份同内容的 4.0 PPT 哈希一致。`manifest.md` 自身不列自引用哈希。
