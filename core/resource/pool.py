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


class ResourceDevice:
    """ 代表所有测试资源设备的配置类，字段动态定义

    Attributes:
        port: 字典，用以保存设备端口对象DevicePort的实例
    """

    def __init__(self, name="", *args, **kwargs):
        self.name = name
        self.type = kwargs.get("type", None)
        self.description = kwargs.get("description", None)
        self.ports = dict()

    def add_port(self, name, *args, **kwargs):
        if name in self.ports:
            # 以 f开头表示在字符串内支持大括号内的python表达式
            raise Exception(f"Port Name {name} already exists")
        self.ports[f"{name}"] = DevicePort(self, name, args, kwargs)

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


class DevicePort:
    """ 代表设备的连接端口
    Attributes:
        parent: 用以保存其父的对象实例
    """

    def __init__(self, parent_device=None, name="", *args, **kwargs):
        self.parent = parent_device
        self.name = name
        self.description = kwargs.get("description", None)
        self.remote_ports = list()

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
                ret[key] = list()
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

    Attributes:
        (待补全)
    """

    def __init__(self):
        """
        0ResourcePool的初始化函数
        """
        self.topology = dict()
        self.information = dict()
        self.file_name = None
        self.reserved = None

    def add_device(self, device_name, **kwargs):
        if device_name in self.topology:
            raise ResourceError(f"devide {device_name} already exists")
        self.topology[device_name] = ResourceDevice(device_name)

    def reserve(self):
        """
        给文件添加reserved字段（所有者， 操作日期）的信息，用以进行排他性控制
        [警告]: 执行前要先读取文件,以保证从前一次读取到执行reserve方法之间没有其他人占用该资源
        TODO: 防君子不防小人, 仅作为一种通知机制,修改文件的字段函数即失效, 可在后续进行完善
        @return:
        """
        if self.file_name is None:
            raise ResourceError("load a resource file first")
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
            raise ResourceError("load a resource file first")
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
            raise ResourceError(f"Cannot find file {filename}")

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
            raise ResourceError(f"Resource is reserved by {json_object['reserved']['owner']}")

        self.owner = owner

    def load(self, filename):
        """
        @param filename:文件名
        @return:
        """
        # 检查文件是否存在
        if not os.path.exists(filename):
            raise ResourceError(f"Cannot find file {filename}")

        # 初始化
        self.topology.clear()
        self.reserved = False
        self.information = dict()

        # 读取资源配置的JSON字符串
        with open(filename) as file:
            json_object = json.load(file)

        # 对JSON字符串进行序列化操作
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

    def save(self, filename):
        with open(filename, mode="w") as file:
            root_object = dict()
            root_object['device'] = dict()
            root_object['info'] = self.information
            for device_key, device in self.topology.items():
                root_object['device'][device_key] = device.to_dict()
            json.dump(root_object, file, indent=4)

    def collect_device(self, device_type, count):
        """
        获取资源设备信息
        @param device_type: 获取的资源设备的信息
        @param count: 获取的资源设备的数量
        @return:
        """
        ret = list()
        for key, value in self.topology.items():
            if value.type == device_type:
                ret.append(value)
            if len(ret) > count:
                return ret
        else:
            return list()

if __name__ == '__main__':
    switch = ResourceDevice(name="switch1")
    switch.add_port("ETH1/1")
    switch.add_port("ETH1/2")

    switch2 = ResourceDevice(name="switch2")
    switch2.add_port("ETH1/1")
    switch2.add_port("ETH1/2")

    switch.ports['ETH1/1'].remote_ports.append(switch2.ports['ETH1/1'])
    switch2.ports['ETH1/1'].remote_ports.append(switch.ports['ETH1/1'])

    print(json.dumps(switch.to_dict(), indent=4))
