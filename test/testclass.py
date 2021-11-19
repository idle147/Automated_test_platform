# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 20:34
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: testclass.py
from core.config.setting import SettingBase, dynamic_setting


@dynamic_setting
class TestClass:
    def __init__(self, *args, **kwargs):
        self.setting_path = kwargs.get("setting_path", ".")
        self.setting_file = kwargs.get("setting_file", None)

    class MySetting(SettingBase):
        """
        MySetting是针对TestClass类的配置类, 类中类的优势如下
        1. 在定义类的同时,将相应的配置项清晰地定义出来,比较只管
        2. 不同的类的配置类可以定义成相同的名字, 不会冲突
        """
        field1 = 1
        field2 = 2


tc = TestClass(setting_path=".")
