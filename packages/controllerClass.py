import os, random, pickle, time
from packages import cardClass, personClass

# 操作控制类
class controller():
    # 数据存储格式
    userIdCardIdDict = {}      # {身份证ID: 银行卡ID}
    cardIdUserObjDict = {}     # {银行卡ID: 用户对象}

    # 数据存储的URL
    userFileURL = './databases/user.txt'
    cardFileURL = './databases/card.txt'

    def __init__(self):
        # 加载所有的数据信息
        self.__loadData()

    # 1 注册
    def register(self):
        # 获取用户输入的用户名、身份证号、手机号、密码
        userName = self.__getUserInfo('用户名')
        userId = self.__getUserInfo('身份证号')
        # 检测身份证号是否已存在
        if userId in self.userIdCardIdDict:
            print(f'当前用户已存在，卡号为：{self.userIdCardIdDict[userId]}。')
            return
        phone = self.__getUserInfo('手机号')
        pwd = self.__getUserInfo('预设密码')

        # 创建卡号
        while True:
            cardId = random.randint(100000, 999999)
            if cardId in self.cardIdUserObjDict:
                continue
            break
        # 创建银行卡对象
        cardObj = cardClass.card(cardId, pwd)

        # 创建用户对象，绑定银行卡
        userObj = personClass.person(userName, userId, phone, cardObj)

        # 创建需要保存的数据格式
        # userIdCardIdDict = {} {身份证ID: 银行卡ID}
        # cardIdUserObjDict = {} {银行卡ID: 用户对象}
        self.userIdCardIdDict[userId] = cardId
        self.cardIdUserObjDict[cardId] = userObj

        # 开户成功
        self.__log(f'用户<{userName}>开户成功！卡号：{cardId} 余额：{cardObj.balance}。')

        self.__saveData()

    # 2 查询
    def query(self):
        # 由卡号获取卡对象
        cardObj = self.__getCardObj()
        if not cardObj:
            return

        # 验证是否锁卡
        if cardObj.isLocked:
            print(f'当前银行卡已冻结，无法操作，请联系管理员。')
            return

        # 验证密码
        if not self.__checkPwd(cardObj):
            return

        # 验证通过显示查询到的余额
        self.__log(f'您当前查询的卡号：{cardObj.cardId}，余额：{cardObj.balance}元。')

    # 3 存款
    def addMoney(self):
        # 由卡号获取卡对象
        cardObj = self.__getCardObj('转入卡号')
        if not cardObj:
            return

        # 存款并显示
        moneySaved = float('%.2f' % float(input('请存入金额：')))
        cardObj.balance += moneySaved
        self.__log(f'存款成功，指定卡号<{cardObj.cardId}>内存入{moneySaved}元。')

        self.__saveData()

    # 4 取款
    def getMoney(self):
        # 由卡号获取卡对象
        cardObj = self.__getCardObj()
        if not cardObj:
            return

        # 验证是否锁卡
        if cardObj.isLocked:
            print('当前银行卡已冻结，无法操作，请联系管理员。')
            return

        # 验证密码
        if not self.__checkPwd(cardObj):
            return

        # 验证通过取款并显示余额
        moneyWithdrew = self.__withdrawMoney(cardObj)
        if moneyWithdrew:
            self.__log(f'取钱成功，指定卡号<{cardObj.cardId}>内取出{moneyWithdrew}元，'
                       f'余额：{cardObj.balance}元。')

        self.__saveData()

    # 5 转账
    def transferMoney(self):
        # 由转出卡号获取卡对象
        cardOutObj = self.__getCardObj()
        if not cardOutObj:
            return

        # 验证转出卡是否锁卡
        if cardOutObj.isLocked:
            print('当前银行卡已冻结，无法操作，请联系管理员。')
            return

        # 验证转出卡密码
        if not self.__checkPwd(cardOutObj):
            return

        # 由转入卡号获取卡对象
        cardInObj = self.__getCardObj('转入卡号')
        if not cardInObj:
            return

        # 存款并显示
        moneyWithdrew = self.__withdrawMoney(cardOutObj)
        if moneyWithdrew:
            cardInObj.balance += moneyWithdrew
            self.__log(f'转账成功，指定卡号<{cardOutObj.cardId}>向'
                       f'卡号<{cardInObj.cardId}>转账{moneyWithdrew}元，'
                       f'转出卡内的余额：{cardOutObj.balance}元。')

        self.__saveData()

    # 6 改密
    def changePwd(self):
        # 由卡号获取卡对象
        cardObj = self.__getCardObj()
        if not cardObj:
            return

        # 验证是否锁卡
        if cardObj.isLocked:
            print('当前银行卡已冻结，无法操作，请联系管理员。')
            return

        # 选择输入原密码或者提供身份证改密
        getOption = input('两种方式可供改密服务：\n'
                          '(1) 验证原密码 (2) 提供身份证 (其他) 返回上层\n'
                          '请选择：')
        if not ((getOption == '1' and self.__checkPwd(cardObj)) or \
            (getOption == '2' and self.__checkUserId(cardObj))):
            return

        # 更新密码
        while True:
            pwd = self.__getUserInfo('预设密码')
            if pwd == cardObj.pwd:
                print('预设密码与原密码相同，请重新输入。')
                continue
            cardObj.pwd = pwd
            break

        self.__saveData()

    # 7 锁卡
    def lockCard(self):
        # 由卡号获取卡对象
        cardObj = self.__getCardObj()
        if not cardObj:
            return

        # 验证是否锁卡
        if cardObj.isLocked:
            print('当前银行卡已冻结，无需再次锁卡。')
            return

        # 验证身份证信息
        if self.__checkUserId(cardObj):
            self.__lockThisCard(cardObj)
        self.__saveData()

    # 8 解卡
    def unlockCard(self):
        # 由卡号获取卡对象
        cardObj = self.__getCardObj()
        if not cardObj:
            return

        # 验证是否锁卡
        if not cardObj.isLocked:
            print('当前银行卡未被冻结，可正常操作。')
            return

        # 验证身份证解锁
        if self.__checkUserId(cardObj):
            cardObj.isLocked = False
            self.__log(f'银行卡<{cardObj.cardId}成功解锁，余额：{cardObj.balance}元。>')

        self.__saveData()

    # 9 补卡
    def newCard(self):
        # 由身份证找出用户对象和原卡对象
        userId = self.__getUserInfo('身份证号')
        if userId not in self.userIdCardIdDict:
            print('初次办卡，无需补卡，请移步注册。')
            return
        oriCardId = self.userIdCardIdDict[userId]
        userObj = self.cardIdUserObjDict[oriCardId]

        # 创建新卡号
        while True:
            newCardId = random.randint(100000, 999999)
            if newCardId in self.cardIdUserObjDict:
                continue
            break
        # 预设密码
        newPwd = self.__getUserInfo('预设密码')
        # 获取原卡余额
        balance = userObj.card.balance
        # 创建新卡对象
        newCardObj = cardClass.card(newCardId, newPwd, balance)
        # 更新userIdCardIdDict和cardIdUserObjDict
        self.userIdCardIdDict[userId] = newCardId
        userObj.card = newCardObj
        self.cardIdUserObjDict[newCardId] = userObj
        del self.cardIdUserObjDict[oriCardId]
        self.__log(f'您的旧卡<{oriCardId}>作废，新卡<{self.cardIdUserObjDict[newCardId].card.cardId}>创办成功，余额：'
                   f'{self.cardIdUserObjDict[newCardId].card.balance}元。')

        self.__saveData()

    # 0 退出
    def save(self):
        print('欢迎下次登陆。')

    # 加载数据库中的用户和银行卡信息
    def __loadData(self):
        # 检测文件是否存在
        if not (os.path.exists(self.cardFileURL) and
            os.path.exists(self.userFileURL)):
            return
        with open(self.cardFileURL, 'rb') as fd:
            self.userIdCardIdDict = pickle.load(fd)
        with open(self.userFileURL, 'rb') as fd:
            self.cardIdUserObjDict = pickle.load(fd)
        print('数据加载完毕。')

    # 获取注册用户信息的私有方法
    # 参数userInfoType可为'身份证号'、'手机号'、'预设密码'、'本人卡号'、'转入卡号'
    def __getUserInfo(self, userInfoType):
        while True:
            userInfo = input(f'请输入您的{userInfoType}：')
            # 判断用户输入的信息是否有效，身份证必须18位数字，手机必须11位数字，密码必须6位数字
            if not userInfo or\
                (userInfoType == '身份证号' and (userInfo.isdigit() == False or len(userInfo) != 8)) or\
                (userInfoType == '手机号' and (userInfo.isdigit() == False or len(userInfo) != 11)) or\
                (userInfoType == '预设密码' and (userInfo.isdigit() == False or len(userInfo) != 6)) or\
                ((userInfoType == '本人卡号' or userInfoType == '转入卡号') and\
                 (userInfo.isdigit() == False or len(userInfo) != 6)):
                print(f'您输入的{userInfoType}不合法，请重新输入。')
                continue

            # 预设密码需再次确认
            if userInfoType == '预设密码':
                rePwd = input('请再次输入预设密码以确认：')
                if rePwd != userInfo:
                    print('两次输入密码不一致，请重新设置密码。')
                    continue
                print('密码设置成功。')
            return userInfo

    # 由卡号搜索卡对象
    # cardType 参数可为'本人卡号'（默认值）、'转入卡号'
    def __getCardObj(self, cardType = '本人卡号'):
        # 获取用户输入的卡号
        while True:
            cardId = int(self.__getUserInfo(cardType))

            # 验证卡号是否存在
            if cardId in self.cardIdUserObjDict:
                return self.cardIdUserObjDict[cardId].card
            # 卡号不存在，选择重新输入或者退出
            getOption = input('当前卡号不存在，是否重新输入？\n'
                  '(1) 重新输入 (其他) 返回上层\n'
                  '请选择：')
            if getOption == '1':
                continue
            return None

    # 核对密码信息是否正确
    def __checkPwd(self, cardObj):
        # 获取用户输入的密码，用户有3次输入机会
        pwdErrCnt = 0
        while True:
            pwdInput = input('请输入银行卡密码：')
            if pwdInput == cardObj.pwd:
                return True
            pwdErrCnt += 1
            if pwdErrCnt < 3:
                print(f'密码输入错误，您还有{3 - pwdErrCnt}次机会，请重新输入。')
                continue

            # 输入密码错误达到3次，冻结银行卡
            self.__lockThisCard(cardObj)
            break
        return False

    # 验证身份证信息是否正确
    def __checkUserId(self, cardObj):
        userIdInput = input('请输入身份证：')
        if userIdInput == (self.cardIdUserObjDict[cardObj.cardId]).userId:
            return True
        print('身份证信息验证失败，退出操作。')
        return False

    # 由当前卡对象取钱，成功返回取出金额，失败返回None
    def __withdrawMoney(self, cardObj):
        while True:
            moneyWithdrew = float('%.2f' % float(input('请输入预取出或转账的金额：')))
            if moneyWithdrew <= cardObj.balance:
                cardObj.balance -= moneyWithdrew
                return moneyWithdrew
            getOption = input('预取出或转账金额超出当前银行卡余额，是否重新输入？\n'
                              '(1) 重新输入 (其他) 返回上层\n'
                              '请选择：')
            if getOption == '1':
                continue
            return None

    # 保存用户信息和银行卡信息
    def __saveData(self):
        # 把当前数据写入文件中
        with open(self.cardFileURL, 'wb+') as fd:
            pickle.dump(self.userIdCardIdDict, fd)

        with open(self.userFileURL, 'wb+') as fd:
            pickle.dump(self.cardIdUserObjDict, fd)

    def __lockThisCard(self, cardObj):
        cardObj.isLocked = True
        self.__log(f'当前银行卡<卡号：{cardObj.cardId}>被冻结，请联系管理员。')

    def __log(self, logStr):
        # 日志打屏
        print(logStr)

        # 设置日志存放路径
        logFileURL = './databases/log.txt'

        # 设置日志格式 '[2022-02-05 12:12:12] xxx'
        newLogStr = time.strftime('[%Y-%m-%d %H:%M:%S] ') + logStr + '\n'

        with open(logFileURL, 'a+', encoding = 'utf-8') as fd:
            fd.write(newLogStr)