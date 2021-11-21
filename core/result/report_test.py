# -*- coding:utf-8 -*-
# @Time: 2021/11/20 0020 16:33
# @Type: Unit Test
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: report_test.py
import pytest


# =====================================
# pytest用例设计原则
#   1. 文件名以test_*.py文件和*_test.py
#   2. 以test_开头的函数
#   3. 以Test开头的类，test_开头的方法，并且不能带有__init__ 方法
#   4. 所有的包pakege必须要有__init__.py文件
#   5. 断言使用assert
# =====================================


class TestClass:

    def test_one(self):
        x = "this"
        assert 'h' in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, 'check')

    def test_three(self):
        a = "hello"
        b = "hello world"
        assert a in b


if __name__ == "__main__":
    pytest.main('-q test_class.py')
