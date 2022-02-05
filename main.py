# import os
from packages import viewClass, controllerClass

class main():
    def __init__(self):
        # 实例化视图对象
        viewObj = viewClass.views()
        # 实例化操作控制类
        controlObj = controllerClass.controller()

        while True:
            # 显示操作界面
            # os.system('clear')  # windows清屏
            viewObj.showFunc()

            # 让用户选择操作
            funcNum = input('请输入您要选择的操作：')
            # 需要验证用户的输入是否正确
            if funcNum not in [f'{i}' for i in range(10)]:
                print('您输入的内容有误，请重新输入。')
                continue

            funcDict = {'1': 'register', '2': 'query',
                        '3': 'addMoney', '4': 'getMoney',
                        '5': 'transferMoney', '6': 'changePwd',
                        '7': 'lockCard', '8': 'unlockCard',
                        '9': 'newCard', '0': 'save'}
            eval(f'controlObj.{funcDict[funcNum]}()')
            if funcNum == '0':
                break

if __name__ == '__main__':
    main()