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
from core.resource.pool import ResourceError, register_resource


# TODO: 此处写需要实例化的接口对象, 如ssh, telnet。

def create_ssh(resource):
    ip = resource.management.get("ip", "")
    port = resource.management.get("port", 23)
    # TODO: 返回一个实例化对象
    #   return SSHClient(ip, port, username, password)
    return


register_mapping = (
    ("device", "ssh", create_ssh)
)

# 注册资源
for mapping in register_mapping:
    register_resource(mapping[0], mapping[1], mapping[2])
