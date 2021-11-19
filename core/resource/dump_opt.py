# _*_ coding: utf-8 _*_
"""
@File: dump_opt.py
@Time: 2021/6/19 0019 21:38
@Author: Yu Yangxin
@Description: 管理资源设备类
"""
from abc import ABCMeta, abstractmethod, ABC


class DumpInterface():
    """ 序列化操作的接口
    父类: [接口]让子类具体实现序列化操作
    """
    __metaclass__ = ABCMeta  # 指定这是一个抽象类

    @abstractmethod  # 纯虚, 必须实现
    def to_dict(self):
        """
        序列化函数, 由子类具体实现
        """
        pass

    @classmethod
    def from_dict(cls):
        """
        反序列化函数, 由子类具体实现
        """
        pass


class DevicePort(DumpInterface):
    """ 端口类

    实现端口类的相关属性

    Attributes:
        (待补全)
    """

    def __init__(self):
        """
        DevicePort(DumpInterface)的初始化函数
        """
        pass

    def to_dict(self):
        pass

    @staticmethod
    def from_dict():
        pass


class ResourceDevice(DumpInterface):
    """ 资源配置类

    代表所有自测资源设备的配置类,字段动态定义

    """

    def __init__(self):
        """
        ResourceDevice的初始化函数
        """
        pass

    def to_dict(self):
        """序列化
        将配置文件序列化成字典格式
        @return: 序列化后的字典
        """
        ret = dict()
        # 利用迭代的思想, 输入ret
        for key, value in self.__dict__.items():
            # 如果是端口, 端口下有多个子端口, 转换成字典
            if key == 'ports':
                ret[key] = dict()
                # 对每个子端口, 进行序列化
                for port_name, port in value.items():
                    ret[key][port_name] = port.to_dict()
            else:
                ret[key] = value
        return ret

    @staticmethod
    def from_dict(dict_obj):
        """ 反序列化
        将字典类型的数据反向转换成相应的类对象
        @param dict_obj: 需要反序列化的字典对象
        @return: ResourceDevice的实例
        """
        ret = ResourceDevice()
        for key, value in dict_obj.items():
            if key == "ports":
