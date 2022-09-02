# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 10:43
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: precondition.py
from abc import ABCMeta, abstractmethod

from core.result.reporter import StepResult, ResultReporter
from .base import TestType


# =====================================
# 前置条件判断:
#   1. 用很多if语句则会导致代码难以维护
#   2. 将其设为标准接口类, 让开发者完成不同的实现
# =====================================
class PreConditionBase(metaclass=ABCMeta):
    """
    前置条件判断基类
    """

    @abstractmethod
    def is_meet(self, test_case, result_report: ResultReporter):
        """
        通过传入的测试用例进行前置条件的判断
        @param test_case:
        @param result_report:
        @return:
        """
        pass

    @abstractmethod
    def get_description(self):
        """
        返回这个条件的描述信息
        @return:
        """
        pass


class IsTestCaseType(PreConditionBase):
    """
    判断测试用例是否是指定的类型
    """

    def __init__(self, expected_type):
        self.case_type = expected_type

    def is_meet(self, test_case, result_report: ResultReporter):
        ret = test_case.test_type & self.case_type > 0
        if ret:
            result_report.add(StepResult.INFO,
                              self.get_description())
        else:
            result_report.add(
                StepResult.INFO,
                f"{self.get_description()},当前测试用例类型是{test_case.test_type}",
            )

        return ret

    def get_description(self):
        return f"测试用例的类型必须是{TestType(self.case_type).name}"


class IsTestCasePriority(PreConditionBase):
    """
    判断测试用例是否是指定的优先级
    """

    def __init__(self, expected_priority):
        self.priority = expected_priority

    def is_meet(self, test_case, result_report: ResultReporter):
        ret = test_case.priority in self.priority
        if ret:
            result_report.add(StepResult.INFO, self.get_description())
        else:
            result_report.add(StepResult.INFO, self.get_description(), + f",当前测试用例优先级是{test_case.priority}")
        return ret

    def get_description(self):
        return f"测试用例的优先级必须是{self.priority}"


class IsPreCasePassed(PreConditionBase):
    """
    判断前置测试用例是否是某个期望的结果
    """

    def __init__(self, result_list):
        self.result_list = result_list  # 用来记录已经执行的测试用例的结果信息

    def is_meet(self, test_case, result_report: ResultReporter):
        if not any(test_case.pre_tests):
            # 没有前置测试用例，直接返回真
            return True

        # 遍历前置测试用例清单, 并从测试完成结果集中查找测试用例执行结果
        # 结果集查无该测试用例, 则返回False
        # 一旦有一个结果没有成功执行则返回False
        # TODO: 此处查找算法可进行优化, 如二分等
        for pre_case in test_case.pre_tests:
            for case, data in self.result_list.items():
                if pre_case == case:
                    if data['result']:
                        break
                    result_report.add(StepResult.INFO, f"{case}的执行结果不成功")
                    return False
            else:
                result_report.add(StepResult.INFO, f"{pre_case}没有执行")
                return False

        # 全部执行则返回True
        result_report.add(StepResult.INFO, self.get_description())
        return True

    def get_description(self):
        return "前置测试用例运行结果必须为通过"


class IsHigherPriorityPassed(PreConditionBase):
    """
    高优先级测试用例全部通过
    """

    def __init__(self, priority, result_list):
        self.priority = priority
        self.result_list = result_list

    def is_meet(self, test_case, result_report: ResultReporter):
        if not test_case.skip_if_high_priority_failed:
            return True
        #  遍历测试用例结果集, 判断是否存在高优先级未成功执行的测试用例
        for case, data in self.result_list.items():
            if data['priority'] < self.priority and not data["result"]:
                result_report.add(StepResult.INFO, f"测试用例{case}没有执行成功")
                return False
        result_report.add(StepResult.INFO, self.get_description())
        return

    def get_description(self):
        return f"优先级{self.priority}以上的测试用例必须通过"
