# -*- coding:utf-8 -*-
# @Time: 2021/11/20 0020 13:31
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: time_tool.py
import time


class TimeTool:
    @classmethod
    def get_time_stamp(cls):
        ct = time.time()
        local_time = time.localtime(ct)
        # 时间格式化
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        time_stamp = data_head
        # data_secs = (ct - int(ct)) * 1000
        # time_stamp = "%s.%03d" % (data_head, data_secs)
        # 去除下划线和空格
        # stamp = ("".join(time_stamp.split()[0].split("-")) +
        #         "".join(time_stamp.split()[1].split(":"))).replace('.', '')
        # print(stamp)
        return time_stamp
