# _*_ coding: utf-8 _*_
# @Time : 2021/6/19 0019 20:51
# @Author : Yu Yangxin
# @File : pool.py
# @desc : 测试资源——序列化与反序列化
"""
    测试资源池
    ~~~~~~~~~~~
    一组测试资源的合集,测试平台可以对测试资源池进行统一的管理,我们可以给测试资源池设计一些功能,提供给测试用例开发者调用
"""
import json
import os
import time
from abc import ABCMeta, abstractmethod

from core.config.setting import static_setting, SettingBase

# =====================================
# 配置接口:管理测试资源的接口, 是代码用来向测试资源发送和接收信息的重要途径
# 方法: 1. 对响应的库进行实例化, 需要调用的时候再进行封装(使用回调函数)
#      2. 实例化的方法不传递任何参数,把需要调用的方法提前注册,生成资源类型和实例化方法之间的映射关系
# =====================================
# 保存资源类型和实例化方法的映射关系
_resource_device_mapping = {}
_resource_port_mapping = {}


class ResourceError(Exception):
    """
    自定义异常处理
    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):  # 异常的字符串信息
        return self.message


class ResourceNotMeetConstraint(Exception):
    def __init__(self, constraints):
        super().__init__("Resource Not Meet Constraints")
        self.description = ""
        for constraint in constraints:
            self.description += constraint.description + "\n"


def register_resource(category, resource_type, comm_callback):
    """
    注册配置接口实例化的方法或类
    @param category:
    @param resource_type:
    @param comm_callback:
    @return:
    """
    if category == "device":
        _resource_port_mapping[resource_type] = comm_callback
    elif category == "port":
        _resource_port_mapping[resource_type] = comm_callback


def get_resource_pool(filename, owner):
    ResourceSetting.load()
    full_name = os.path.join(ResourceSetting.resource_path, filename)
    rv = ResourcePool()
    rv.load(full_name, owner)
    return rv


class ResourceDevice:
    """ 代表所有测试资源设备的配置类，字段动态定义

    Attributes:
        port: 字典，用以保存设备端口对象DevicePort的实例
    """

    def __init__(self, name="", *args, **kwargs):
        self.name = name
        self.type = kwargs.get("type", None)
        self.description = kwargs.get("description", None)
        self.pre_connect = False
        self.ports = {}
        self._instance = None

    def get_comm_instance(self, new=False):
        """
        获取资源句柄
        @param new: 是否需要预先建立资源的管理实例
        @return: 资源管理实例化句柄
        """
        # 判断类型是否进行过实例化注册
        if self.type not in _resource_device_mapping:
            raise ResourceError(f"资源类型 {self.type} 尚未注册")
        # 是否需要预先建立资源的管理实例
        if not new and self._instance:  # 不需要建立
            return self._instance
        else:  # 需要建立
            self._instance = _resource_device_mapping[self.type](self)
        return self._instance

    def add_port(self, name, *args, **kwargs):
        if name in self.ports:
            # 以 f开头表示在字符串内支持大括号内的python表达式
            raise Exception(f"端口名[ {name} ]已经存在")
        self.ports[f"{name}"] = DevicePort(self, name, args, kwargs)

    def get_port_count(self, **kwargs):
        return len(self.ports)

    def to_dict(self):
        ret = dict()
        for key, value in self.__dict__.items():
            if key == "ports":
                ret[key] = dict()
                for port_name, port in value.items():
                    ret[key][port_name] = port.to_dict()  # 调用DevicePort采用迭代的思想获取端口的实例化结果
            else:
                ret[key] = value
        return ret

    @staticmethod
    def from_dict(dict_obj):
        """
        @param
            dict_obj: 序列化后的字符串
        @return
            序列化后的对象
        """
        ret = ResourceDevice()
        for key, value in dict_obj.items():
            if key == "ports":
                ports = dict()
                for port_name, port in value.items():
                    ports[port_name] = DevicePort.from_dict(port, ret)
                setattr(ret, key, value)
            else:
                setattr(ret, key, value)
        return ret


@static_setting.setting("ResourceSetting")
class ResourceSetting(SettingBase):
    """资源配置模块的配置类
    当资源模块被引用时,会执行装饰器函数,将该类自动添加到static_setting的setting属性中
    """
    file_name = "resource_setting.setting"
    resource_path = os.path.join(os.getcwd(), "test_resource")
    auto_connect = False


class DevicePort:
    """ 代表设备的连接端口
    Attributes:
        parent: 用以保存其父的对象实例
    """

    def __init__(self, parent_device=None, name="", *args, **kwargs):
        self.parent = parent_device
        self.name = name
        self.type = kwargs.get("type", None)
        self.description = kwargs.get("description", None)
        self.remote_ports = []
        self._instance = None

    def get_comm_instance(self, new=False):
        if self.type not in _resource_port_mapping:
            raise ResourceError(f"type {self.type} is not registered")
        if not new and self._instance:
            return self._instance
        else:
            self._instance = _resource_port_mapping[self.type](self)
        return self._instanc

    def to_dict(self):
        """序列化方法

        传统的序列化方法__dict__: 1.无法实例化类实例所对应的内存地址; 2.在做反序列化的时候无法确定实例的类型; 3. 无法递归处理
        解决方法: 循环遍历所有的属性,如果需要parent和remote_port字段,则特殊处理。只存储parent的名称,以及远端端口实例化的parent和端口名称,以避免递归

        @return:
            序列化对象
        """
        ret = dict()
        for key, value in self.__dict__.items():
            if key == "parent":
                ret[key] = value.name
            elif key == "remote_ports":
                ret[key] = []
                for remote_port in value:
                    # 使用device的名称和port的名称来表示远端的端口
                    # 在反序列化的时候可以方便地找到相应的对象实例
                    ret[key].append(
                        {
                            "device": remote_port.parent.name,
                            "port": remote_port.name
                        }
                    )
            else:
                ret[key] = value
        return ret

    @staticmethod
    def from_dict(dict_obj, parent):
        """ 反序列化方法
        
        @param
            dict_obj: 序列化后的字符串
        @return
            序列化后的对象
        """
        ret = DevicePort(parent)
        # 除remote_ports和parent外,将字典中所有的key设置成该实例的属性
        for key, value in dict_obj.items():
            if key == "remote_ports" or key == "parent":
                continue
            setattr(ret, key, value)  # 设置属性值
        return ret


class ResourcePool:
    """ 资源池类
    负责资源的序列化和反序列化
    """

    def __init__(self):
        """
        0ResourcePool的初始化函数
        """
        self.topology = {}  # 存放资源的字典
        self.information = {}
        self.file_name = None
        self.reserved = None
        self.owner = None

    def add_device(self, device_name, **kwargs):
        if device_name in self.topology:
            raise ResourceError(f"设备[ {device_name} ]已经存在")
        self.topology[device_name] = ResourceDevice(device_name)

    def reserve(self):
        """
        给文件添加reserved字段（所有者， 操作日期）的信息，用以进行排他性控制
        [警告]: 执行前要先读取文件,以保证从前一次读取到执行reserve方法之间没有其他人占用该资源
        TODO: 防君子不防小人, 仅作为一种通知机制,修改文件的字段函数即失效, 可在后续进行完善
        @return:
        """
        if self.file_name is None:
            raise ResourceError("首次载入资源文件")
        self.load(self.file_name, self.owner)
        self.reserved = {"owner": self.owner,
                         "date": time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                         }
        self.save(self.file_name)

    def release(self):
        """
        确保文件是被当前操作者所占用,然后用清空reserved属性,并调用save方法
        @return:
        """
        if self.file_name is None:
            raise ResourceError("首次载入资源文件")
        self.load(self.file_name)
        self.reserved = None
        self.save(self.file_name)

    def load(self, filename, owner):
        """
        加载资源(不对资源进行处理),同时判断是否是当前的拥有者
        @param filename: 文件名
        @param owner: 拥有者
        @return:
        """
        # 检查文件是否存在
        if not os.path.exists(filename):
            raise ResourceError(f"无法找到文件[ {filename} ]")

        # 初始化
        self.file_name = filename
        self.topology.clear()
        self.reserved = False
        self.information = dict()

        # 读取资源配置的JSON字符串
        with open(filename) as file:
            json_object = json.load(file)

        # 判断是否被占用(不是当前的所有者)
        if "reserved" in json_object and \
                json_object['reserved'] is not None and \
                json_object['reserved']['owner'] != owner:
            raise ResourceError(f"源文件已经被[ {json_object['reserved']['owner']} ]占用")

        self.owner = owner

        if "info" in json_object:
            self.information = json_object['info']
        for key, value in json_object['devices'].items():
            device = ResourceDevice.from_dict(value)
            self.topology[key] = device

        # 映射所有设备的连接关系
        for key, device in json_object['devices'].items():
            for port_name, port in device['ports'].items():
                for remote_port in port['remote_ports']:
                    remote_port_obj = self.topology[remote_port["device"]].ports[remote_port["port"]]
                    self.topology[key].ports[port_name].remote_ports.append(remote_port_obj)

    # def load(self, filename):
    #     """
    #     @param filename:文件名
    #     @return:
    #     """
    #     # 检查文件是否存在
    #     if not os.path.exists(filename):
    #         raise ResourceError(f"查无文件[ {filename} ]")
    #
    #     # 初始化
    #     self.topology.clear()
    #     self.reserved = False
    #     self.information = dict()
    #
    #     # 读取资源配置的JSON字符串
    #     with open(filename) as file:
    #         json_object = json.load(file)
    #
    #     # 对JSON字符串进行序列化操作
    #     if "info" in json_object:
    #         self.information = json_object['info']
    #     for key, value in json_object['devices'].items():
    #         device = ResourceDevice.from_dict(value)
    #         self.topology[key] = device
    #
    #     # 映射所有设备的连接关系
    #     for key, device in json_object['devices'].items():
    #         for port_name, port in device['ports'].items():
    #             for remote_port in port['remote_ports']:
    #                 remote_port_obj = self.topology[remote_port["device"]].ports[remote_port["port"]]
    #                 self.topology[key].ports[port_name].remote_ports.append(remote_port_obj)

    def save(self, filename):
        with open(filename, mode="w") as file:
            root_object = dict()
            root_object['device'] = dict()
            root_object['info'] = self.information
            for device_key, device in self.topology.items():
                root_object['device'][device_key] = device.to_dict()
            json.dump(root_object, file, indent=4)

    def collect_device(self, device_type, count, constraints=[]):
        """
        获取 指定数量的 资源设备信息
        @param device_type: 获取的资源设备的信息
        @param count: 获取的资源设备的数量
        @param constraints: 约束类对象, 对测试资源进行合法性校验
        @return:
        """
        ret = []
        for key, value in self.topology.items():
            if value.type == device_type:
                # 判断测试资源是否符合相应的约束
                for constraint in constraints:
                    if not constraint.is_meet(value):
                        break
                else:
                    ret.append(value)
            if len(ret) > count:
                return ret
        else:  # 如果条件一直不满足，则执行该语句
            return []

    def collect_device(self, device_type, constraints=[]):
        """
        获取所有的资源设备信息
        @param device_type: 获取的资源设备的信息
        @param count: 获取的资源设备的数量
        @return:
        """
        ret = []
        for key, value in self.topology.items():
            if value.type == device_type:
                # 判断测试资源是否符合相应的约束
                for constraint in constraints:
                    if not constraint.is_meet(value):
                        break
                else:
                    ret.append(value)
        return ret

    def collect_connection_route(self, resource, constraints=list()):
        """
        获取资源连接路由
        """
        # 限制类必须是连接限制ConnectionConstraint
        for constraint in constraints:
            if not isinstance(constraint, ConnectionConstraint):
                raise ResourceError(
                    "collect_connection_route only accept ConnectionConstraints type")
        ret = []
        for constraint in constraints:
            conns = constraint.get_connection(resource)
            if not any(conns):
                raise ResourceNotMeetConstraint([constraint])
            for conn in conns:
                ret.append(conn)
        return ret


class Constraint(metaclass=ABCMeta):
    """
    资源选择器限制条件的基类
    """

    def __init__(self):
        self.description = None

    @abstractmethod
    def is_meet(self, resource, *args, **kwargs):
        pass


class ConnectionConstraint(Constraint, metaclass=ABCMeta):
    """
    用户限制获取Remote Port的限制条件。
    """

    @abstractmethod
    def get_connection(self, resource, *args, **kwargs):
        pass


@static_setting.setting("ResourceSetting")
class ResourceSetting(SettingBase):
    file_name = "resource_setting.setting"

    resource_path = os.path.join(os.environ['HOME'], "test_resource")
    auto_connect = False


if __name__ == '__main__':
    # 创建实例化对象
    switch = ResourceDevice(name="switch1")
    switch.add_port("ETH1/1")
    switch.add_port("ETH1/2")

    switch2 = ResourceDevice(name="switch2")
    switch2.add_port("ETH1/1")
    switch2.add_port("ETH1/2")

    switch.ports['ETH1/1'].remote_ports.append(switch2.ports['ETH1/1'])
    switch2.ports['ETH1/1'].remote_ports.append(switch.ports['ETH1/1'])

    rp = ResourcePool()
    rp.topology['switch1'] = switch
    rp.topology['switch2'] = switch2
    # rp.save("test.json")
    rp.load("test.json", "michael")
    rp.reserve()
    rp2 = ResourcePool()
    rp2.load("test.json", "jason")
    print("done")
