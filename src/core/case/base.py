# -*- coding:utf-8 -*-
# @Time: 2021/11/21 0021 21:27
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: base.py.py
from abc import abstractmethod, ABCMeta
from enum import IntEnum


class TestType(IntEnum):
    UNIT = 1
    SANITY = 2
    FEATURE = 4
    REGRESSION = 8
    SYSTEM = 16
    ALL = 255


class TestCaseBase(metaclass=ABCMeta):
    """
    测试用例基类
    RFT(rational function code_test): 三步走
        setup: 用来进行测试过程的配置
        code_test: 具体的测试过程
        cleanup: 恢复测试的配置,测试对象恢复初始状态
    """

    def __init__(self, reporter):
        self.reporter = reporter
        self._output_var = {}
        self.setting = None
        self.logger = reporter.case_logger
        self.test_data_var = {}
        self.result = None

    @abstractmethod
    def collect_resource(self, pool):
        """
        Collect Test Resource
        """
        pass

    @abstractmethod
    def setup(self, *args):
        pass

    @abstractmethod
    def test(self, *args):
        pass

    @abstractmethod
    def cleanup(self, *args):
        pass

    @property
    def output_var(self):
        """
        测试用例输出变量, 能够让测试引擎收集
        :return:
        """
        return self._output_var

    def get_setting(self, setting_path, setting_file):
        """
        在测试用例中引用setting字段来读取配置
        """
        for k, v in self.__class__.__dict__.items():
            if hasattr(v, "__base__") and v.__base__.__name__ == "TestSettingBase":
                self.setting = v(setting_path, setting_file)
                self.setting.load()
