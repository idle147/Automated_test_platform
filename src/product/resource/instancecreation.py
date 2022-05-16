# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 13:31
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: instancecreation.py
"""
    接口实例化的注册方法
    测试资源模块的耦合点
"""
from core.resource.pool import register_resource, ResourcePool
from third_part.commandline.ssh import SshClient
from third_part.commandline.telnet import TelnetClient


# =====================================
# create_telnet和create_ssh这两个方法是用来实例化SSH和Telnet配置接口,
# 通过regitser_resource方法进行注册,测试用例开发工程师,可以根据测试项目中用到的测试设备,
# 自行添加各种资源类型到配置接口实例化方法的映射关系中。
# =====================================
def create_telnet(resource):
    ip = resource.management.get("ip", "")
    port = resource.management.get("port", 23)
    username = resource.management.get("username", "")
    password = resource.management.get("password", "")
    return TelnetClient(ip, port, username, password)


def create_ssh(resource):
    ip = resource.management.get("ip", "")
    port = resource.management.get("port", 23)
    username = resource.management.get("username", "")
    password = resource.management.get("password", "")
    return SshClient(ip, port, username, password)


if __name__ == '__main__':
    # 数据准备
    register_mapping = (
        ("device", "telnet", create_telnet),
        ("device", "ssh", create_ssh),
    )

    # 注册资源
    for mapping in register_mapping:
        register_resource(mapping[0], mapping[1], mapping[2])

    # 资源池操作
    rp = ResourcePool()
    rp.add_device("TelnetServer1", type="telnet")  # 往资源池内添加资源设备
    # 设置资源的具体属性
    setattr(rp.topology["TelnetServer1"], "management",
            {"ip": "192.168.1.100",
             "port": 23,
             "username": "admin",
             "password": "admin"}
            )
    # 获取符合约束的资源
    telnet_resource = rp.collect_device_info(device_type="telnet", count=1)[0]
    # 获取具体资源的实例化句柄
    telnet_client = telnet_resource.get_comm_instance()
    print(telnet_client.host)
