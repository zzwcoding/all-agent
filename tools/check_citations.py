#!/usr/bin/env python3
"""check_citations.py —— ID 引用清单逐条比对检具（All-agent 票 13；审查一 P2）。

契约：check_citations.py <答案md>
对一份 semantic-service 形态的答案 markdown：
  1. 以固定节标记「本回答引用的元素 ID」（skills/semantic-service 的
     id-citation-format.md §3 定名的答案末尾固定节）为界切分正文与清单节；
  2. 抽取正文中的 ID token（通用大写前缀形态，不绑域：段式
     XXX-YYY-ZZZ…，首段全大写 ≥2 字符，后段字母/数字——覆盖 AGG-/BH-/RULE-/
     QR-/GLS-/SCR- 等任意注册或自定义前缀；MENU-01 等两段形态不算元素 ID）；
  3. 与清单节内的 ID token 集合逐个比对，双向差异都报：
     正文有清单无（清单不完备）/ 清单有正文无（清单注水）。

「清单是答案 ID 的完备登记」本是 id-citation-format.md 的纸面纪律（该文自认
机读断言面，票 07 实际只断言清单节存在），本检具把它落成机械闸（票 13）。

退出码：0 正文与清单一致；1 不一致（有双向差异任一）；2 用法错误（缺参/文件不可读）。
注意：本检具只做「正文↔清单一致」比对；「答案必须至少引用一个 ID」是
skill 工序纪律（无 ID 可引该走拒答），不在本工具判定面。

确定性、零 LLM；只读。依赖：Python3 stdlib。
"""

import re
import sys
from pathlib import Path

LIST_MARKER = "本回答引用的元素 ID"

# ID token：首段全大写字母 ≥2 个，随后 ≥2 个连字段（每段=纯数字，如 001/01，
# 或大写字母开头的字母数字段，如 BOHAI/RecordDailyOutput）。ASCII 边界
# lookaround 防误切（20260911-T3 的 T-3、QR-X-001x 的尾部粘字母均不命中；
# 紧贴中文汉字不算边界内字符，照常命中）。
ID_TOKEN = re.compile(
    r"(?<![A-Za-z0-9-])[A-Z]{2,}(?:-\d+|-[A-Z][A-Za-z0-9]*){2,}(?![A-Za-z0-9-])")


def split_answer(text: str) -> tuple[str, str]:
    """按清单节标记切分（标记所在行首起为清单节）；无标记则正文=全文、清单节为空。"""
    idx = text.find(LIST_MARKER)
    if idx < 0:
        return text, ""
    line_start = text.rfind("\n", 0, idx) + 1
    return text[:line_start], text[line_start:]


def extract_tokens(text: str) -> set[str]:
    return set(ID_TOKEN.findall(text))


def compare(path: Path) -> tuple[bool, str]:
    """返回 (是否一致, 人读报告)。"""
    text = path.read_text(encoding="utf-8")
    body, listing = split_answer(text)
    body_tokens = extract_tokens(body)
    list_tokens = extract_tokens(listing)
    only_body = sorted(body_tokens - list_tokens)
    only_list = sorted(list_tokens - body_tokens)
    lines = [
        f"引用清单比对 — {path}",
        f"正文 ID token（去重）: {len(body_tokens)} 个；清单节 ID token（去重）: "
        f"{len(list_tokens)} 个",
    ]
    if only_body:
        lines.append("正文有清单无（清单不完备）: " + "、".join(only_body))
    if only_list:
        lines.append("清单有正文无（清单注水）: " + "、".join(only_list))
    ok = not only_body and not only_list
    lines.append("结论: 一致" if ok else "结论: 不一致")
    return ok, "\n".join(lines)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print("用法: check_citations.py <答案md>\n"
              "  比对答案正文与「本回答引用的元素 ID」清单节的 ID token，"
              "双向差异都报。\n"
              "  退出码: 0 一致 / 1 不一致 / 2 用法错误", file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.is_file():
        print(f"用法错误: 文件不存在或不可读: {path}", file=sys.stderr)
        return 2
    ok, report = compare(path)
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
