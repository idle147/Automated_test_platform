# -*- coding:utf-8 -*-
# @Time: 2021/11/20 0020 13:31
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: time_tool.py
import time


class TimeTool:
    @staticmethod
    def get_local_time():
        return time.strftime("%B %d, %y %H:%M:%S", time.localtime())

    @staticmethod
    def get_time_stamp():
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
