import time

class views():
    def __init__(self):
        self.__showIndex()
        print('系统正在加载，请稍后...')
        time.sleep(1)

    # 显示欢迎界面
    def __showIndex(self):
        varStr = '''\
************************************************
*                                              *
*                                              *
*               Welcome to Bank                *
*                                              *
*                                              *
************************************************\
'''
        print(varStr)

    # 显示操作界面
    def showFunc(self):
        varStr = '''\
************************************************
*          (1) 注册           (2) 查询          *
*          (3) 存款           (4) 取款          *
*          (5) 转账           (6) 改密          *
*          (7) 锁卡           (8) 解卡          *
*          (9) 补卡           (0) 退出          *
************************************************\
'''
        print(varStr)

if __name__ == '__main__':
    views()