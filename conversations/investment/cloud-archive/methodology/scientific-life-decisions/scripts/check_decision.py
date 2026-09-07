#!/usr/bin/env python3
"""Check v2/v3 decision records and optional v3 state consistency, never truth."""

import argparse
import json
from pathlib import Path
import re
import sys

HEADINGS = (
    "1. 问题、目标与约束",
    "2. 本次使用的方法",
    "3. 证据、假设与未知",
    "4. 方案与取舍",
    "5. 反对理由与敏感性",
    "6. 建议、条件与下一步",
    "7. 复核与证据缺口",
    "8. 结果跟踪",
)
METHODS = {f"M{i:02d}" for i in range(1, 24)}
STATES = {"待补证", "条件建议", "建议可供选择", "已决定"}
EMPTY = {"", "待填写", "待填", "TODO", "TBD", "...", "……", "-", "{{}}"}


def field(text, key):
    # A blank field must not consume the next line's text as its value.
    values = re.findall(rf"^{re.escape(key)}[：:][ \t]*(.*?)[ \t]*$", text, re.M)
    return values[0] if len(values) == 1 else None


def validate(text, state_record=None):
    errors = []
    # Quoted or fenced examples do not count as actual sections or metadata.
    visible_lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence is None and not line.lstrip().startswith(">"):
            visible_lines.append(line)
    clean = "\n".join(visible_lines)
    if re.search(r"\{\{.*?\}\}", text, re.S):
        errors.append("仍含模板占位项 {{...}}。未知应明确说明及其影响。")
    for key in ("协议版本", "记录编号", "记录类型", "建议状态", "阻断性缺口"):
        value = field(clean, key)
        if value is None or value.strip() in EMPTY:
            errors.append(f"字段缺失、重复或未填写：{key}")
    version = field(clean, "协议版本")
    if version not in {"2.0", "3.0"}:
        errors.append("协议版本必须为2.0或3.0。")
    state = field(clean, "建议状态")
    if state not in STATES:
        errors.append("建议状态不在允许范围内。")
    if version == '3.0':
        if state == '已决定':
            errors.append('3.0将用户选择与建议状态分开，已决定不是建议状态。')
        for key in ('输入版本', '用户选择', '执行状态', '状态记录'):
            value = field(clean, key)
            if value is None or value.strip() in EMPTY:
                errors.append(f'3.0缺少字段：{key}')
        if state_record is None:
            errors.append('3.0完整记录须用--state提供结构化状态，不能只作Markdown检查。')
        else:
            from decision_engine import evaluate
            try:
                result = evaluate(state_record)
                errors.extend(result['record_issues'])
                expected = {
                    '记录编号': state_record['decision_id'],
                    '输入版本': str(state_record['revision']),
                    '建议状态': state_record['recommendation']['status'],
                    '用户选择': state_record['user_choice']['status'],
                    '执行状态': state_record['execution']['status'],
                }
                for key, value in expected.items():
                    if field(clean, key) != value:
                        errors.append(f'Markdown与JSON不一致：{key}')
                if result['blocking_issues'] and field(clean, '阻断性缺口') == '无':
                    errors.append('JSON仍有阻断项，Markdown不能写阻断性缺口无。')
            except (ValueError, TypeError) as exc:
                errors.append(f'状态记录无效：{exc}')
    if state == "建议可供选择" and field(clean, "阻断性缺口") != "无":
        errors.append("仍有阻断性缺口时不能标为建议可供选择。")
    if field(clean, "记录类型") not in {"实际决策", "合成示例"}:
        errors.append("记录类型必须是实际决策或合成示例。")
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", clean, re.M))
    sections = {}
    for i, match in enumerate(matches):
        title = match.group(1)
        if title in sections:
            errors.append(f"重复章节：{title}")
        stop = matches[i + 1].start() if i + 1 < len(matches) else len(clean)
        sections[title] = clean[match.end():stop].strip()
    for title in HEADINGS:
        if title not in sections or sections[title].strip() in EMPTY:
            errors.append(f"章节缺失或未填写：{title}")
    method_section = sections.get(HEADINGS[1], "")
    ids = set(re.findall(r"(?<![A-Za-z0-9_])M\d{2}(?![A-Za-z0-9_])", method_section))
    invalid = ids - METHODS
    if invalid:
        errors.append("未知方法编号：" + ", ".join(sorted(invalid)))
    missing = {"M01", "M05", "M23"} - ids
    if missing:
        errors.append("缺少基础方法编号：" + ", ".join(sorted(missing)))
    evidence = sections.get(HEADINGS[2], "")
    for key in ("来源", "日期"):
        value = field(evidence, key)
        if value is None or value.strip() in EMPTY:
            errors.append(f"证据章节需要填写汇总字段：{key}")
    for title, key in ((HEADINGS[6], "复核方式"), (HEADINGS[7], "复盘触发条件")):
        value = field(sections.get(title, ""), key)
        if value is None or value.strip() in EMPTY:
            errors.append(f"章节需要填写字段：{key}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="要检查的 Markdown 决策记录")
    parser.add_argument('--state', type=Path, help='3.0结构化状态文件')
    args = parser.parse_args()
    try:
        text = args.file.read_text(encoding="utf-8")
        state_record = json.loads(args.state.read_text(encoding='utf-8')) if args.state else None
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"无法读取文件：{exc}", file=sys.stderr)
        return 2
    errors = validate(text, state_record)
    if errors:
        print("结构检查未通过：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("基本结构检查通过。")
    if state_record is not None:
        from decision_engine import evaluate
        result = evaluate(state_record)
        print('记录支持的建议状态：' + result['supported_recommendation_status'])
        print('下一阶段：' + result['next_stage'])
        print('阻断项数：' + str(len(result['blocking_issues'])))
    print("这不验证证据真实、方法正确、计算无误或建议准确；不构成现实行动许可。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
