# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 18:10
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: setting.py
"""
    配置类：
        1. 方便地扩展和定义：我们能够在一个基类上通过继承来实现对配置的扩展，比如不同模块的不同配置项
        2. 实现保存和读取功能：能够将配置类中所有的字段保存到文件，同时能够读通过读取方法来装载配置
"""
import json
import os
from abc import ABCMeta
from functools import wraps

_DEFAULT_PATH = os.path.join(os.getcwd(), "test_config")  # environ['HOME']就代表了当前这个用户的主目录


class SettingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# =====================================
# 提供了基本的save方法和load方法，可以通过继承SettingBase类来实现自己的配置类
# =====================================
class SettingBase(metaclass=ABCMeta):
    """
    配置基类
    """
    file_name = None
    setting_path = _DEFAULT_PATH

    @classmethod
    def _get_full_path(cls):
        """
        当配置文件的文件名为空时,生成一个文件名,否则按默认路径(_DEFAULT_PATH)生成
        @return:
        """
        filename = cls.file_name if cls.file_name else cls.__name__ + ".settings"
        return os.path.join(cls.setting_path, filename)

    @classmethod
    def save(cls):
        """
        将对象序列化输出成配置文件
        @return:
        """
        # 判断文件是否存在, 不存在则创建
        if not os.path.exists(cls.setting_path):
            os.makedirs(cls.setting_path)

        # 序列化操作
        with open(cls._get_full_path(), "w") as file:
            obj = {}
            for key, value in cls.__dict__.items():
                # 过滤掉诸如__module__等以"_"开头的信息，setting_path字段，file_name字段
                # TODO: 此处可进行其他非法字符串的过滤操作
                if key.startswith("_") or key == "setting_path" or key == "file_name":
                    continue
                obj[key] = value
            json.dump(obj, file, indent=4)

    @classmethod
    def load(cls):
        if os.path.exists(cls._get_full_path()):
            # 文件存在,读取并赋值
            with open(cls._get_full_path()) as file:
                obj = json.load(file)
            for key, value in obj.items():
                setattr(cls, key, value)
        else:
            cls.save()  # 文件不存在则通过save方法生成默认配置文件


# =====================================
# 静态配置:键值对形式
#   为了将配置统一的进行管理,将[配置管理对象]作为一个单例
#   其他模块被引用时, 将其配置类添加到配置管理对象中
# =====================================
class StaticSettingManager:
    """
    静态配置管理类
    """

    def __init__(self):
        self.settings = {}
        self._setting_path = _DEFAULT_PATH

    def add_setting(self, setting_name, setting_class):
        """
        注册开发者自己实现的配置类
        @param setting_name:
        @param setting_class:
        @return:
        """
        if hasattr(setting_class, "__base__"):
            if setting_class.__base__.__name__ != "SettingBase":
                raise SettingError("注册的配置必须是SettingBase的子类")
        else:
            raise SettingError("注册的配置必须是SettingBase的子类")
        # 将该类添加到字典当中, 同时使用当前的setting_path来设置类的setting_path
        self.settings[setting_name] = setting_class
        setting_class.setting_path = self._setting_path

    def setting(self, setting_name, *args, **kwargs):
        """
        配置文件的注册装饰器
        @param setting_name:
        @param args:
        @param kwargs:
        @return:
        """

        def wrapper(cls):
            self.add_setting(setting_name, cls)
            return cls

        return wrapper

    """
    @property装饰器: 既要保护类的封装特性，又要让开发者可以使用“对象.属性”的方式操作操作类属性
    应用场景: 在获取、设置和删除对象属性的时候，需要额外做一些工作。比如在游戏编程中，设置敌人死亡之后需要播放死亡动画。
    目的: 在赋值的同时更新所有已注册的配置类的setting_path信息 
    """

    @property
    def setting_path(self):
        return self._setting_path  # setting_path属性是个只读属性

    @setting_path.setter
    # 可修改的setting_path属性
    def setting_path(self, value):
        self._setting_path = value
        # 更改所有的对象的配置路径
        for key, setting in self.settings.items():
            setting.setting_path = value

    def sync_path(self):
        """
        同步所有的配置
        @return:
        """
        for key, setting in self.settings.items():
            setting.setting_path = self._setting_path

    def save_all(self):
        """
        保存所有的配置
        @return:
        """
        for key, setting in self.settings.items():
            setting.save()

    def load_all(self):
        """
        读取所有的配置
        @return:
        """
        self.sync_path()
        for key, setting in self.settings.items():
            setting.load()


# =====================================
# 动态配置: 在类的实例执行过程中添加参数设置
#   配置是针对特定的类生效
#   配置文件和路径是可以通过外部传入来设置的
#   类实例化的过程中, 要生成相应的字段(比如settings)来保存配置类
# 方法: 在类中添加继承自SettingBase的配置类来实现,并使用该装饰器来添加实例化过程中对配置的初始化和装载
# =====================================
def dynamic_setting(cls):
    @wraps(cls)  # 解决函数的名字变成装饰器中的包装器导致的原函数属性失效问题
    def inner(*args, **kwargs):
        """这个装饰器用于需要添加配置的类，在类的实例化过程中调用

        @param args:
        @param kwargs:
        @return:
        """
        rv = cls(*args, **kwargs)
        for key, value in cls.__dict__.items():
            # 对被装饰的类的__dict__进行判断, 找到父类为SettingBase的类
            if hasattr(value, "__base__") and value.__base__.__name__ == "SettingBase":
                setattr(rv, "setting", value)  # 将该类设置成该类实例的一个属性

                # 判断类实例中是否存在setting_path和setting_file的属性
                if hasattr(rv, "setting_path"):
                    value.setting_path = rv.setting_path
                if hasattr(rv, "setting_file") and rv.setting_file is not None:
                    value.file_name = rv.setting_file

                # 如果没有则使用默认值
                if value.file_name is None:
                    value.file_name = f"{cls.__name__}_{value.__name__}.setting"
                else:
                    value.file_name = f"{cls.__name__}_{value.file_name}.setting"
                value.load()
        return rv

    return inner


# =====================================
# 带逻辑功能的配置:
#   作用场景: 测试用例执行前后或者执行时所需要的配置, 或者执行的过程
#   通过统一的输入参数实现自己的业务逻辑, 然后通过统一的管理工具来管理其装载,提供给测试引擎统一调用
#   代码路径: core/config/module.py
# =====================================


static_setting = StaticSettingManager()
