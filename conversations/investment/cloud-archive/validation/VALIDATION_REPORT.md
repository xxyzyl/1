# VALIDATION_REPORT.md — 打包与基线验证

## 已执行验证

- 现行方法源码测试：`python3 -m unittest discover -s methodology/scientific-life-decisions/scripts -p 'test_*.py' -v`。
- 系统控制算例：`python3 methodology/scientific-life-decisions/scripts/system_control_examples.py --self-test`。
- 示例资源账：`examples/resources-over-budget.json` 和 `examples/resources-shared-work.json` 已用 `check_life_resources.py` 校验。
- PPT 文本已提取到 `context/presentation-text/`，原 PPT 保留在 `artifacts/presentations/`。
- 图片产物在打包前做了文件存在和基础读取检查；此前被截断的协作图已使用修复版本。

## 验证结果

现有源码快照的决策引擎、资源核算和系统控制算例通过。详细原始输出保存在本目录下的 `package-unittest.stdout.txt`、`package-system-control.stdout.txt`、`example-*.output.json` 和 `SOURCE_BASELINE_VALIDATION.md`。

## 解释边界

这些验证说明方法脚本和示例可以在当前环境运行，不说明完整 Web 产品已经完成。后续本地 Codex 创建 API、数据库和前端后，需要新增端到端测试、权限测试、幂等测试和多用户隔离测试。
