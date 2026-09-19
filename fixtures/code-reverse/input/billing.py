# 出厂集固定输入（合成）· fixtures/code-reverse/input/billing.py
# 「图书借阅管理」逾期计费件：常量约束（超期上限/日罚/暂停线）→规则候选、
# ReaderStatus 字面量集合→字典候选、函数间真实调用→调用链素材。
# 票 31 定稿后不改；改动 = 出厂集破坏性变更，须重新核对 expected-output/。
from library import Loan
class ReaderStatus:
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
MAX_OVERDUE_DAYS = 30  # 超期天数上限（常量约束素材）
FINE_PER_DAY = 0.5  # 日罚款额
SUSPEND_FINE = 20.0  # 暂停借阅的未缴罚款线
def overdue_days(due_date, return_date):
    return max(0, (return_date - due_date).days)
def calc_fine(days):
    if days > MAX_OVERDUE_DAYS:
        days = MAX_OVERDUE_DAYS  # 罚款天数按上限封顶
    return days * FINE_PER_DAY
def refresh_status(reader, unpaid_fine):
    if unpaid_fine >= SUSPEND_FINE:
        reader.status = ReaderStatus.SUSPENDED
    else:
        reader.status = ReaderStatus.ACTIVE
def settle_return(loan: Loan, return_date):
    days = overdue_days(loan.due_date, return_date)
    fine = calc_fine(days)  # 真实调用：settle_return → calc_fine
    loan.close(return_date)  # 真实调用：settle_return → Loan.close（跨文件）
    return fine
