# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 21:21
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: module.py
import json
import os
from abc import ABCMeta, abstractmethod
from enum import Enum
from importlib import import_module
from threading import Thread

from core.config.setting import static_setting, SettingBase
from core.resource.pool import ResourcePool
from core.result.reporter import ResultReporter


class ModuleType(Enum):
    PRE = 1  # 表示在测试用例执行前运行该模块
    PARALLEL = 2  # 表示该模块和测试用例同步执行
    POST = 3  # 表示在测试用例执行完毕后执行该模块


# =====================================
# 提供了action方法和stop方法,供开发者实现自己的功能
# =====================================
class ModuleBase(metaclass=ABCMeta):
    """逻辑配置模块的基类
    模块的开发者通过调用这些实例,对测试资源进行操作并输出结果
    """
    module_type = None
    priority = 99

    def __init__(self, report: ResultReporter, resource: ResourcePool):
        self.reporter = report
        self.resource = resource
        self.thread = None  # 保存并行执行的模块的执行线程

    @abstractmethod
    def action(self):
        """
        通过该方法来实现模块的逻辑功能
        @return:
        """
        pass

    def do(self):
        # 若是并行,则新建线程
        # TODO: 未考虑锁机制
        if self.module_type == ModuleType.PARALLEL:
            self.thread = Thread(target=self.action)
            self.thread.start()
        else:
            self.action()

    @abstractmethod
    def stop(self):
        """
        通过该方法来实现模块逻辑功能的终止
        @return:
        """


# =====================================
# 问题: 针对逻辑配置模块, 不同的功能也需要不同的参数, 这些参数不能统一提供
# 解决: 给逻辑配置加上动态配置功能
# =====================================
@static_setting.setting("LogicModule")
class ModuleSetting(SettingBase):
    """逻辑配置模块
    1. 逻辑配置模块管理器 读取 配置晚间
    2. 将相应的模块通过动态引用储存在管理器中
    3. 当测试执行模块需要使用模块的时候, 管理器将 配置模块类 实例化, 并返回给 测试执行模块
    """
    module_list_file = "./modules/module_list.json"  # 逻辑配置模块列表清单(测试执行工程师决定)
    module_setting_path = "./modules/settings"


# =====================================
# 逻辑配置模块通过ModuleManager进行统一管理
# 测试执行者配置逻辑模块配置列表, 管理器读取配置列表, 并动态地引用相应地模块
# =====================================
class ModuleManager:
    """
    配置模块的管理
    """

    def __init__(self):
        self.modules = {}  # 用以保存装载的逻辑配置类

    def load(self):
        """
        从模块列表装载所有模块类
        @return:
        """
        if not os.path.exists(ModuleSetting.module_list_file):
            # 如果查无,则不做操作
            return
        with open(ModuleSetting.module_list_file) as file:
            obj = json.load(file)

        for item in obj['modules']:
            try:
                # 配置条目格式
                # {
                #   "name": "模块名",
                #   "package": "模块路径",
                #   "setting_file": "模块动态配置文件名",
                #   "setting_path": "模块动态配置文件路径"
                # }
                module_name = item['name']
                module_package = item['package']
                setting_file = item.get("setting_file", None)
                setting_path = item.get("setting_path", ModuleSetting.module_setting_path)
                m = import_module(module_package)  # 动态导入对象
                for element, value in m.__dict__.iters():
                    # 将符合要求的类及其对应的配置文件信息保存在modules中
                    if element == module_name:
                        self.modules[module_name] = {
                            "class": value,
                            "setting_file": setting_file,
                            "setting_path": setting_path
                        }
            except Exception:
                pass

    def add_module(self, module_class, setting_file=None, setting_path=None):
        """添加模块
        向管理器添加新的逻辑配置类, 它可以与用户操作模块相结合, 配合save方法来配置和保存模块列表
        @param module_class:
        @param setting_file:
        @param setting_path:
        @return:
        """
        obj = {
            "class": module_class,
            "setting_file": setting_file,
            "setting_path": setting_path
        }
        self.modules[module_class.__name__] = obj

    def get_module_instances(self, module_type, result_reporter, resources):
        """获取模块的实例化列表
        具体的实例需要在测试执行时, 通过提供资源配置实例及其测试报告实例来创建相应的实例。
        @param module_type:
        @param result_reporter: 测试报告
        @param resources: 资源配置实例
        @return:
        """
        rv = []
        for mkey, mvalue in self.modules.items():
            if mvalue['class'].module_type.value == module_type.value:
                rv.append(mvalue['class'](result_reporter, resources))
        return rv

    def save(self):
        """
        将所有模块信息保存到模块配置列表
        @return:
        """
        obj = {}
        obj['modules'] = []
        for mkey, mvalue in self.modules.items():
            obj['modules'].append({
                "name": mkey,
                "package": mvalue["class"].__module__,
                "setting_file": mvalue["setting_file"],
                "setting_path": mvalue["setting_path"]
            })

        file_dir = os.path.dirname(ModuleSetting.module_list_file)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(ModuleSetting.module_list_file, "w") as file:
            json.dump(obj, file, indent=4)
