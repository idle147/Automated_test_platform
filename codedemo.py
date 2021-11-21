# -*- coding:utf-8 -*-
# @Time: 2021/11/20 0020 13:48
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: codedemo.py
import os


class MyClass(object):

    @staticmethod
    def static_method_one():
        print("cmd_one \t")

    @staticmethod
    def _get_dot_line(line, line_max):
        length = len(line)
        if length >= line_max:
            return "-" * length
        else:
            return "-" * (line_max - length)

    def static_method_two(self):
        ret = "cmd_two \n"
        ret += self._get_dot_line(ret, 5)
        print(ret)


# C = MyClass()
# C.static_method_two()

print(os.getcwd())
