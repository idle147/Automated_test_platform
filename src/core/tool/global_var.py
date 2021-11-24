# -*- coding:utf-8 -*-
# @Time: 2021/11/20 0020 21:44
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: global_var.py
import threading

"""
线程安全的单利模式

紧跟with后面的语句被求值后，返回对象的 __enter__() 方法被调用，这个方法的返回值将被赋值给as后面的变量。
当with后面的代码块全部被执行完之后，将调用前面返回对象的 __exit__()方法
"""


def synchronized(func):
    """
    优点：第一次调用才初始化，避免内存浪费。
    缺点：必须加锁 synchronized 才能保证单例，但加锁会影响效率。
    @param func:
    @return:
    """
    func.__lock__ = threading.Lock()

    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return lock_func


class GlobalVar(object):
    instance = None

    @synchronized
    def __new__(cls, *args, **kwargs):
        # 如果类属性instance的值为None，那么就创建一个对象
        if not cls.instance:
            cls.instance = super(GlobalVar, cls).__new__(cls)
        # 如果已经有实例存在，直接返回
        return cls.instance

    def __init__(self):
        # 初始化一个全局的字典
        GlobalVar.global_dict = {}

    @staticmethod
    def set_value(key, value):
        GlobalVar.global_dict[key] = value

    @staticmethod
    def get_value(key):
        try:
            return GlobalVar.global_dict[key]
        except KeyError as e:
            print(e)


GlobalVar()
GlobalVar.set_value("TIME_FORMAT", "%Y-%m-%d %H:%M:%S")
print(GlobalVar.get_value("TIME_FORMAT"))
