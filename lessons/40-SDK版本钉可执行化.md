# 施工日志 40 · MCP SDK 版本钉可执行化

日期: 2026-09-20
角色: L2 编码（自主档）
票: tickets/40-SDK版本钉可执行化.md（AC 真源=票面 AC 表；设计裁决 L0 已定，照办）
因由: docs/第三期B线拆票方案.md 批次一；docs/二期收官报告.md §6 #4 + 票 37 注记（「mcp==2.2.0 实测钉在 docs/mcp-server.md，SDK 升级须重跑票 24 smoke」从文档注记落成可执行面）。
交接包注记: 主窗口防踩坑 7 条逐条照办（钉版文件内容逐字照抄/检出抽纯函数/--strict 语义/文档对齐/CI 免疫红线/边界照 Touches/完成自查逐条实证），下文留证。

## 做了什么

1. **钉版文件落位**：`tools/requirements-mcp.txt`——`mcp==2.2.0` 真源行 + 两行注释（venv 安装命令原文、升级纪律：改版本号 → 重跑票 24 smoke client `--full` 9/9 → 更新本文件与 docs/mcp-server.md）。内容按交接包原文逐字落盘。
2. **布局登记**：references/repo-layout.json tools 条目 patterns 增 `requirements*.txt`（purpose/producer/顶层 description 同步注记票 40；实跑归档闸驱动，同票 30 手法）。归档闸受管全集含 untracked（`git ls-files --others`），新文件不做布局登记即 CI 红——登记先行，实跑验证。
3. **启动版本检出（提示性非硬闸）**：semantic_mcp_server.py 新增「版本检出」节——
   - `_installed_mcp_version()`：`importlib.metadata.version("mcp")`，未装返回 None（PackageNotFoundError 收敛）；
   - `_read_pin(pin_path)`：逐行剥注释/空白后匹配 `^mcp==(\S+)$`，缺失/不可读（OSError 族含 IsADirectoryError）/无钉版行 → None；
   - `_version_verdict(installed, pin_path) -> (警告|None, 是否不符)`：一致 → (None, False)；不符 → 警告「已装 mcp X ≠ 钉版 2.2.0——核对 docs/mcp-server.md；继续启动（--strict 可改为强退）」+ (警告, True)；钉版缺失类 → 降级警告「跳过版本核对继续启动」+ (警告, False)；
   - `check_version(installed, pin_path=PIN_FILE) -> str | None`：票面指定的模块级纯函数（薄封装 verdict[0]），CLI 无 SDK 也可全路径单测。
4. **--strict CLI 旗标**：main 在 argparse 后、build_server 前薄调用检出——有警告即 stderr 打印；`--strict` 且「不符」（mismatch=True）→ return 2 不起服。降级类（钉版缺失）即使 --strict 也只警告继续——「不符」语义只指版本比对失败，检出是提示性非硬闸（票面「钉版文件缺失→同为警告不崩」+「--strict 时不符即退」两句的合取）。strict 闸挂在 build_server 之前：不符即退，不白构建 server。
5. **单测四路径+（test_semantic_mcp_server.VersionCheckTest，12 例）**：全程注入式不装 mcp——钉版文件 tempfile 写入、已装版本 `mock.patch.object(sms, "_installed_mcp_version")` 注入；strict 路径强制 `_HAS_MCP=True` 走 main（strict 闸先于 build_server，无真 SDK 也不触雷）。四路径：①一致静默（含注释/行尾注释/空行容忍）②不符警告（两版本+≠+docs 指引在场；mismatch=True 与降级类区分；installed=None 也算不符）③--strict 不符 exit 2（main 实跑断言 rc+stderr）+ 降级类 strict 不退 ④钉版缺失/不可读（目录路径）/无钉版行三变体全降级不崩。加例：`test_repo_pin_file_pins_2_2_0`（仓内钉版文件在场且解析恰 2.2.0——AC1 单测面，防钉版文件被改坏后 CI 静默）。
6. **文档对齐**：docs/mcp-server.md 前提节安装命令改 `pip install -r tools/requirements-mcp.txt`，版本钉段改「以 tools/requirements-mcp.txt 为准（当前 2.2.0，实测组合 mcp 2.2.0 + Python 3.11）+ 启动自动检出 + 升级须重跑票 24 smoke 并同步两文件」；运行节增版本检出一行（含 --strict 语义与「降级类仍只警告」）；venv 建议行改 `-r tools/requirements-mcp.txt pyyaml`——PyYAML 不在钉版文件里（票 26 实测不在 mcp 依赖树），纪律保留显式安装。
7. **INSTALL_HINT 增钉版指路**：无 SDK 引导文案加一行钉版安装命令；原文案 `pip install mcp`/`venv`/`docs/mcp-server.md` 字样保留（既有 BootstrapTest 断言零改动零倒）。

## 取舍

- **检出抽 `check_version` 纯函数 + 内部 `_version_verdict` 双返回**：票面钉了 `check_version(...) -> str | None` 签名（返回警告或 None），但 --strict 需要区分「不符」（可升级退 2）与「降级」（永不退）——纯字符串返回值无法机判这个区分，字符串嗅探（如找「≠」）脆。折衷：check_version 按票面签名薄封装，内部 `_version_verdict` 返回 `(警告, mismatch)` 元组给 CLI 用；单测两函数都测，四路径全走 check_version。
- **--strict 不升级降级类**：「不符即退」的字面主语是版本比对；钉版缺失时无钉可比，硬退会把「提示性检出非硬闸」（票面 L0 措辞）变成硬闸，且钉版缺失在 CI/裸 clone 是常态面。裁决：降级一律警告继续，mismatch=False 是机判载体。
- **installed=None 算不符不算静默**：正常流到不了这（无 SDK 先走引导退出 2），但纯函数要自洽——有钉无装是真实的异常态（如 venv 里 pip uninstall 后起服），静默会放过；警告文本用「未检出（mcp 未安装？）」措辞。
- **strict 测试挂 main 而非只测纯函数**：rc=2 是 CLI 行为，纯函数测不出；强制 `_HAS_MCP=True` + mock 版本即可让 main 走到 strict 闸（闸在 build_server 前，无需真 SDK）——比「协议面才能测」的替代方案多出无 SDK 覆盖。
- **不动 smoke client 与 .venv-mcp**：升级纪律的执行载体（票 24 smoke client）零改动；实跑只读用。

## 坑

- **macOS 无 `timeout` 命令**：实跑起步验证改用后台起 + sleep + kill 手法，不留临场文件（验证后即删）。
- **归档闸查 untracked**：受管全集 = `--cached --others --exclude-standard`，新文件提交前就被闸管——「先登记 patterns 再建文件」不是可选步骤，否则本地 ci.sh 当场红。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1 钉版文件在场+布局登记+归档闸绿：tools/requirements-mcp.txt 落盘（内容=交接包原文，含 mcp==2.2.0）；repo-layout.json tools patterns 含 requirements*.txt；`python3 tools/archive_check.py` → 536 文件全对上（含新文件）；单测 test_repo_pin_file_pins_2_2_0 钉解析面（源：本票 AC 表）
- [x] AC2 检出四路径单测：VersionCheckTest 12 例全绿——一致静默/不一致警告/--strict 退出（rc=2+stderr 含 ≠ 与 docs 指引）/钉版缺失降级（缺失/目录不可读/无钉版行三变体）（源：本票 AC 表）
- [x] AC3 docs 对齐：docs/mcp-server.md 安装命令=`pip install -r tools/requirements-mcp.txt`，版本钉段「以钉版文件为准+启动自动检出+升级须重跑票 24 smoke client」成文（源：本票 AC 表）
- [x] AC4 CI：`bash tools/ci.sh` 四闸全绿——闸 1 脚本单测 468 OK（skipped=3 既有协议面占位，456 存量+本票 12）、闸 2 出厂集 14/14、闸 3 边界闸无违规（豁免 9 条不变）、闸 4 归档闸 537 文件全对上（源：CI）
- [x] 加验（交接包 #7 可选项）：.venv-mcp/bin/python 实跑起步——SDK 2.2.0=钉版 2.2.0，stderr 仅就绪横幅零版本警告（一致静默实证）；实弹注入 9.9.9 → --strict rc=2、警告文本逐字核对（「已装 mcp 9.9.9 ≠ 钉版 2.2.0——核对 docs/mcp-server.md；继续启动（--strict 可改为强退）。」）

## 边界自查

改动文件全对齐票面 Touches：tools/requirements-mcp.txt（新）、tools/semantic_mcp_server.py、tools/test_semantic_mcp_server.py、references/repo-layout.json、docs/mcp-server.md、lessons/40。票 24 smoke client（tools/mcp_smoke_client.py）与 .venv-mcp 零改动（实跑只读）；core/graph_index 零改动；既有 server 单测与引导路径零倒（BootstrapTest 3 例原样绿）；无 mcp 环境四闸照常全绿（检出单测全部注入式，CI 未装 mcp）。不 commit（验收与翻 Status 归 L0）。
