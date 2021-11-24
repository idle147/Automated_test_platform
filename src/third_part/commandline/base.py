# -*- coding:utf-8 -*-
# @Time: 2021/11/25 0025 15:55
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: base.py

from abc import ABCMeta, abstractmethod


# from core.resource.pool import register_resource


class CommandLine(metaclass=ABCMeta):

    @abstractmethod
    def send(self, string):
        pass

    @abstractmethod
    def send_and_wait(self, string, waitfor, timeout=60, **kwargs):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def send_binary(self, binary):
        pass

    @abstractmethod
    def receive_binary(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def _login(self):
        pass
