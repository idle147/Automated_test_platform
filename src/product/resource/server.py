# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 13:51
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: server.py
from abc import ABCMeta, abstractmethod

from core.resource.pool import ResourcePool


# =====================================
# 测试资源和配置接口的实例化需要分离(降低耦合)
# 测试资源只负责测试环境静态信息的维护
# 但是我们可以通过回调的方法,将实例化接口提供给其他函数
# =====================================

class Server(metaclass=ABCMeta):
    """
    对服务类型进行抽象
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_resource(self, config_filename, device_type):
        """
        纯虚函数, 用以实现响应的资源方法
        @param config_filename:
        @param device_type:
        @return:
        """
        pass


class SSHServer(Server):
    """
    选择服务为SSH服务
    """

    def __init__(self):
        # 继承父类
        super().__init__()  # 继承父类

    def get_resource(self, config_filename, device_type):
        resource = ResourcePool()
        resource.load(config_filename)
        ssh_device = resource.collect_device(device_type="ssh_server")[0]
        ssh_comm = (ssh_device["ip"], ssh_device["port"],
                    ssh_device["username"], ssh_device["password"])
        return ssh_comm
