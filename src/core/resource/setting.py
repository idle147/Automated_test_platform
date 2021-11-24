# -*- coding:utf-8 -*-
# @Time: 2021/11/25 0025 11:21
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: setting.py
import os

from core.config.setting import static_setting, SettingBase


@static_setting.setting("ResourceSetting")
class ResourceSetting(SettingBase):
    """资源配置模块的配置类
    当资源模块被引用时,会执行装饰器函数,将该类自动添加到static_setting的setting属性中
    """
    file_name = "resource_setting.setting"
    resource_path = os.path.join(os.getcwd(), "test_resource")
    auto_connect = False
