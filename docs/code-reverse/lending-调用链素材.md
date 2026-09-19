# 图书借阅域 代码逆向 · 调用链素材（code-reverse 首份落位示例，票 31）

> 本文件是 code-reverse 调用链素材在实际运行落位（`docs/code-reverse/<域>-调用链素材.md`）的
> 首份示例：内容与出厂集参照产物 fixtures/code-reverse/expected-output/lending-调用链素材.md
> 同源（出厂集 golden 以 fixtures/ 为准，本文件是落位形态的实跑演示，布局表 docs 条目
> code-reverse/*.md 模式随本文件起生效，照票 30 的 docs/requirements 手法）。
> **证据非权威，待 Owner 确认**——本稿全部对象划分、类型占位、关系取舍、行为挂起均为候选，逐条待 Owner 裁决。
> 配套草案域目录见 fixtures/code-reverse/expected-output/lending/（草案只产不进仓，进仓走 MR）。

## 输入概览

- 输入两文件，公开符号 27 个：类 3（Book/Reader/Loan）、字面量集 2（BookStatus/ReaderStatus）、
  方法 4（mark_borrowed/mark_available/can_borrow/close）、函数 4（overdue_days/calc_fine/refresh_status/settle_return）、
  常量约束 4（MAX_BORROW_LIMIT/MAX_OVERDUE_DAYS/FINE_PER_DAY/SUSPEND_FINE）、字段 10。
- 符号覆盖不变量：symbols.txt 逐符号（27 条）必须落三处之一——**草案元素 / 疑点清单 / 明示不逆向清单**，
  逐条落点见末节「符号覆盖对照表」。覆盖探针的判定面 = 该节（从节标题扫到文件尾），
  前文各节是给人读的素材面，不进机判。
- 证据等级：D = 源码结构直证（类/字段/字面量集/常量/调用点）；C = 注释文字；I = 推断
  （类型占位、label 直译、声明/写入分离的归属），I 级逐条标待 Owner 确认。

## 调用链素材（真实调用，逐跳注源）

- 链 1（还书结算，跨文件两跳）：
  - settle_return（billing.py:23）→ Loan.close（library.py:33；调用点 billing.py:26）
  - Loan.close（library.py:33）→ Book.mark_available（library.py:18；调用点 library.py:35）
- 链 2（罚款计算，文件内两步）：
  - settle_return（billing.py:23）→ overdue_days（billing.py:12；调用点 billing.py:24）
  - settle_return（billing.py:23）→ calc_fine（billing.py:14；调用点 billing.py:25）
- 跨文件引用证据：billing.py:5 `from library import Loan` + settle_return 参数标注 loan: Loan
  （billing.py:23）——类型级引用，与链 1 的调用级证据互证。
- 孤儿（无调用点）：Book.mark_borrowed（library.py:16）全库零调用——「借出」动作缺失于调用图，
  不发明调用方，登记疑点 D3。
- 红线边界：调用链只作行为/调用素材，**不产生对象间关联推断**——引用关系只从字段引用推导
  （Loan.book / Loan.reader，library.py:29-30，落 AggregateRootRef）；从调用链引申的关联想象
  一律进疑点清单，不进草案结构。

## 疑点清单（不静默吞，识别即登记）

每条四要素：位置 + 特征 + 源码证据 + 待 Owner 裁决的问题；疑点同时回写草案对应对象 description。

- D1 声明/写入分离：位置 Reader vs refresh_status；特征 status 字段构造器未声明、外部函数直写；
  证据 library.py:20-23（Reader 无 status 声明）vs billing.py:19/21（reader.status = ...）；
  问题——Reader.status 属性按写入点证据立候选（→DICT-LENDING-002，I 级），字段应声明在哪、
  由谁初始化，待 Owner 确认。
- D2 唯一性无声明：位置 book_id / reader_id / loan_id（library.py:13/22/28）；特征命名语义为
  标识符但源码无唯一性约束；问题——属性不标 unique，是否唯一待 Owner 确认。
- D3 孤儿方法：位置 Book.mark_borrowed（library.py:16）；特征全库零调用点；证据调用图扫描
  仅命中「调用链素材」节所列调用；问题——借出链路缺失，方法保留为素材还是死代码剔除，待 Owner 确认。
- D4 类型未注解：位置 due_date / return_date（library.py:31-32）；特征无类型标注；
  证据 billing.py:13 日期差取 days（Date 推断依据）；问题——类型占位 I 级，待 Owner 确认。
- D5 状态判定缺口：位置 can_borrow（library.py:24-25）；特征只判数量上限；
  证据读者暂停状态（ReaderStatus.SUSPENDED）不参与借阅判定，与 RULE-LENDING-003 的暂停口径
  是否要打通源码未给；问题——两处口径是否合并，待 Owner 确认。

## 明示不逆向清单（语言机制/非业务语义，不逆向，带理由）

- `__init__` 构造器本体：语言机制；其字段赋值已按「字段→属性」抽取（library.py:12/21/27），
  不重复立元素。
- import 语句与形参变量（loan / reader / due_date / unpaid_fine 等）：变量不立元素；
  例外——loan: Loan 类型标注是引用证据（已按字段引用落 AggregateRootRef，见草案
  AGG-LENDING-003）。
- 字面量字符串值本身（"AVAILABLE" 等）：存储值进字典 code（D 级直证）；中文 label
  （可借/已借出/丢失/在用/暂停借阅）为直译（I 级），值语义待 Owner 确认。

## 符号覆盖对照表

输入符号（../symbols.txt，27 条）逐条落点。**本节是覆盖探针的判定面**（从本节标题扫到文件尾）：
落点三值 = 草案元素（ID 可指认）/ 疑点清单（D 编号）/ 明示不逆向清单；
表内反引号只用于首列符号名（探针按 `符号` 精确锚定，缺一行即红）。

| 符号 | 输入位置 | 落点 | 草案元素/疑点编号 | 等级 |
|---|---|---|---|---|
| `MAX_BORROW_LIMIT` | library.py:6 | 规则候选 | RULE-LENDING-001 | D |
| `BookStatus` | library.py:7 | 字典候选 | DICT-LENDING-001 | D |
| `Book` | library.py:11 | 对象候选 | AGG-LENDING-001 | D |
| `Book.book_id` | library.py:13 | 属性 | AGG-LENDING-001.bookId | D |
| `Book.title` | library.py:14 | 属性 | AGG-LENDING-001.title | D |
| `Book.status` | library.py:15 | 属性+字典 | AGG-LENDING-001.status → DICT-LENDING-001 | D |
| `Book.mark_borrowed` | library.py:16 | 疑点（孤儿方法）+行为挂起 | 疑点 D3；M2 挂起（omittedModels） | D |
| `Book.mark_available` | library.py:18 | 调用素材+行为挂起 | 调用链 链1 末跳；M2 挂起（omittedModels） | D |
| `Reader` | library.py:20 | 对象候选 | AGG-LENDING-002 | D |
| `Reader.reader_id` | library.py:22 | 属性 | AGG-LENDING-002.readerId | D |
| `Reader.name` | library.py:23 | 属性 | AGG-LENDING-002.name | D |
| `Reader.can_borrow` | library.py:24 | 规则候选（判定来源） | RULE-LENDING-001 | D |
| `Loan` | library.py:26 | 对象候选 | AGG-LENDING-003 | D |
| `Loan.loan_id` | library.py:28 | 属性 | AGG-LENDING-003.loanId | D |
| `Loan.book` | library.py:29 | 引用属性 | AGG-LENDING-003.book → AGG-LENDING-001 | D |
| `Loan.reader` | library.py:30 | 引用属性 | AGG-LENDING-003.reader → AGG-LENDING-002 | D |
| `Loan.due_date` | library.py:31 | 属性 | AGG-LENDING-003.dueDate（类型 I 级，疑点 D4） | D/I |
| `Loan.return_date` | library.py:32 | 属性 | AGG-LENDING-003.returnDate（类型 I 级，疑点 D4） | D/I |
| `Loan.close` | library.py:33 | 调用素材+行为挂起 | 调用链 链1 中跳；M2 挂起（omittedModels） | D |
| `ReaderStatus` | billing.py:6 | 字典候选 | DICT-LENDING-002 | D |
| `MAX_OVERDUE_DAYS` | billing.py:9 | 规则候选 | RULE-LENDING-002 | D |
| `FINE_PER_DAY` | billing.py:10 | 规则候选 | RULE-LENDING-002 | D |
| `SUSPEND_FINE` | billing.py:11 | 规则候选 | RULE-LENDING-003 | D |
| `overdue_days` | billing.py:12 | 规则候选（天数口径） | RULE-LENDING-002 | D |
| `calc_fine` | billing.py:14 | 规则候选（判定来源） | RULE-LENDING-002 | D |
| `refresh_status` | billing.py:18 | 规则候选+状态改写挂起 | RULE-LENDING-003；M2 挂起（omittedModels） | D |
| `settle_return` | billing.py:23 | 调用素材+行为挂起 | 调用链 链1/链2 起点；M2 挂起（omittedModels） | D |

（对照表完毕——27/27 全落点，零静默吞。）
