# ATM
项目说明文档

## 项目基本功能
> 当前的ATM系统模拟实现银行ATM机的操作系统功能
1. 注册
2. 查询
3. 存钱
4. 取钱
5. 转账
6. 改密
7. 锁卡
8. 解卡
9. 补卡
10. 退出

## 项目基本结构
```python
.\ATM\             # 项目目录
│  readMe.md       # 项目文档
│  main.py         # 程序单入口文件
│
├─databases\       # 数据目录
│      user.txt
│      userId.txt
│
└─packages\                 # 包
        cardClass.py        # 银行卡类
        controllerClass.py  # 操作控制类
        personClass.py      # 用户类
        viewClass.py        # 视图显示类
        __init__.py
```

## 运行环境
- 系统：windows/linux/mac
- 版本：python 3.5+
- 其他：无

## 迭代计划
- 增加银行操作日志