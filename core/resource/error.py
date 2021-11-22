# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 15:24
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: error.py
class ResourceNotMeetConstraintError(Exception):
    def __init__(self, constraint):
        super().__init__(constraint.get_description())


class ResourceLoadError(Exception):
    def __init__(self, filename, inner_ex):
        super().__init__("资源文件%s无法读取" % filename)
        self.inner_ex = inner_ex


class ResourceNotRelease(Exception):
    def __init__(self, filename, owner):
        super().__init__("资源文件被占用%s，使用者为%s" % (filename, owner))
