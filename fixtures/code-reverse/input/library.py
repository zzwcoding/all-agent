# 出厂集固定输入（合成）· fixtures/code-reverse/input/library.py
# 中性通用域「图书借阅管理」：书目/读者/借阅单均为通用词，零现实业务域专名。
# 素材四类：类与字段→聚合根/属性候选、方法间真实调用→调用链素材、
# 常量约束→规则候选、状态字面量集合→字典候选。票 31 定稿后不改；
# 改动 = 出厂集破坏性变更，须重新核对 expected-output/ 参照产物。
MAX_BORROW_LIMIT = 5  # 单读者同时在借上限（常量约束素材）
class BookStatus:
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    LOST = "LOST"
class Book:
    def __init__(self, book_id, title):
        self.book_id = book_id
        self.title = title
        self.status = BookStatus.AVAILABLE
    def mark_borrowed(self):
        self.status = BookStatus.BORROWED
    def mark_available(self):
        self.status = BookStatus.AVAILABLE
class Reader:
    def __init__(self, reader_id, name):
        self.reader_id = reader_id
        self.name = name
    def can_borrow(self, active_loans):
        return active_loans < MAX_BORROW_LIMIT
class Loan:
    def __init__(self, loan_id, book, reader, due_date):
        self.loan_id = loan_id
        self.book = book  # 字段引用 Book（引用素材）
        self.reader = reader  # 字段引用 Reader（引用素材）
        self.due_date = due_date
        self.return_date = None
    def close(self, return_date):
        self.return_date = return_date
        self.book.mark_available()  # 真实调用：Loan.close → Book.mark_available
