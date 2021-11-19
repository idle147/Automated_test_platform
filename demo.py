# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 19:18
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: demo.py
from core.config.setting import static_setting
from core.resource.pool import ResourceSetting

static_setting.setting_path = "./user/mySetting"
ResourceSetting.load()

print(f"资源文件路径 {ResourceSetting.resource_path}")
print(f"配置文件路径 {ResourceSetting.setting_path}")

ResourceSetting.resource_path = "./user/new_resource"
static_setting.save_all()
