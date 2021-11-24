# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 11:00
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: constraints.py
from abc import ABCMeta, abstractmethod

from core.resource.pool import ResourceDevice

"""
    资源选择器：对测试资源的合法性进行校验
"""


class Constraint(metaclass=ABCMeta):
    """
    基类：资源选择器限制条件
    """

    def __init__(self):
        self.description = None  # 用来存放对该限制的描述信息

    @abstractmethod
    def is_meet(self, resource, *args, **kwargs):
        """
        纯虚函数：用来判断传入的资源对象是否满足条件
        """
        pass


class ConnectionConstraint(Constraint, metaclass=ABCMeta):
    """
    用户限制获取Remote Port的限制条件。
    """

    @abstractmethod
    def get_connection(self, resource, *args, **kwargs):
        pass


class AndroidConstraint(Constraint):
    """
    判断手机的操作系统是否是安卓机, 可以附带版本大小判断
    """

    def __init__(self, version_op=None, version=None):
        # 继承父类
        super().__init__()  # 继承父类
        self.version_op = version_op
        self.version = version

        # 版本约束
        if self.version_op is not None:
            self.description = f"Phone Type must be Android and version {self.version_op}{version}"
        else:
            self.description = "Phone Type must be Android"

    def is_meet(self, resource, *args, **kwargs):
        # 判断资源类型是否合法
        if isinstance(resource, ResourceDevice) and resource.type == "Android":
            # 判断是否存在版本操作符
            if self.version_op:
                device_version = getattr(resource, "version")
                if device_version is None:
                    return False  # 存在版本操作(version_op)符但不存在版本字段(version),则非法
                # 判断版本操作符与版本字段的关系
                # TODO: 此处未进行详细的版本号比较。如："12.1 > 12.05.02"会报错
                judge_str = f"{device_version}{self.version_op}{self.version}"
                return eval(judge_str)
            else:
                return True
        return False  # 不满足条件


if __name__ == '__main__':
    judge = "12.1 > 12.05.02"
    print(eval(judge))
