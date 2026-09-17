#!/usr/bin/env bash
# ci.sh —— All-agent CI：四个确定性闸，任一红则非零退出。
# 1. 脚本单测（tools/test_*.py，含 schema_check 的 AC1–7 单测）
# 2. 出厂集回归（fixture_run --require-fixtures；schema_check 对 fixtures 最小域+非法变体 = AC1–7）
# 3. 边界闸 skill_deps_check（卡↔脚本依赖一致性；skill 随票 05 起落盘，见脚本内 note）
# 4. 归档闸 archive_check（repo-layout.json + archive-registry.json 两表核对）
# 语义闸本体（schema_check 对 ontology/）由出厂集 AC1 断言承载；渤海域模型文件
# 进仓后（票 05 起），语义闸随本仓 Git MR 流程对 ontology/ 全量跑。
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
step() {
  echo ""
  echo "=== $1 ==="
  shift
  "$@" || fail=1
}

step "脚本单测（tools/test_*.py）" python3 -m unittest discover -s tools -p 'test_*.py' -v
step "出厂集 fixture_run"        python3 tools/fixture_run.py --require-fixtures
step "边界闸 skill_deps_check"   python3 tools/skill_deps_check.py
step "归档闸 archive_check"      python3 tools/archive_check.py

echo ""
if [ "$fail" -eq 0 ]; then
  echo "CI: 全绿"
else
  echo "CI: 有红"
fi
exit "$fail"
