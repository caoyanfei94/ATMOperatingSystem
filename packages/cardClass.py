# 银行卡类
class card():
    def __init__(self, cardId, pwd, balance = 10.00, isLocked = False):
        self.cardId = cardId      # 卡号
        self.pwd = pwd            # 密码
        self.balance = balance    # 余额
        self.isLocked = isLocked  # 是否锁卡，False未锁卡，True锁卡