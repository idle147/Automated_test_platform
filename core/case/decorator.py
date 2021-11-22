# -*- coding:utf-8 -*-
# @Time: 2021/11/21 0021 21:46
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: decorator.py

import inspect
import json
import os
import re
from functools import wraps

from base import TestType
from core.result.reporter import StepResult


class TestDataFileNotFound(Exception):
    pass


class MethodNotFoundError(Exception):
    pass


def case(priority=0, test_type=TestType.ALL, feature_name=None,
         testcase_id=None, pre_tests=None, skip_if_high_priority_failed=False):
    """
    测试用例的装饰器, 用以对测试用例进行基础信息的配置
    """

    def decorator(cls):
        setattr(cls, "priority", priority)  # 测试用例的优先级
        setattr(cls, "test_type", test_type)  # 测试用例的类型
        setattr(cls, "feature_name", feature_name)  # 测试用例测试的功能
        setattr(cls, "testcase_id", testcase_id)  # 测试用例对应的测试用例ID
        setattr(cls, "pre_tests", pre_tests if pre_tests else [])  # 前置的测试用例列表
        setattr(cls, "skip_if_high_priority_failed", skip_if_high_priority_failed)  # 当高优先级失败时,不执行该测试用例
        return cls

    return decorator


def _replace_value(obj, test_case):
    if not isinstance(obj, dict):
        return
    for key, value in obj.items():
        if isinstance(value, str):
            # 替换字符串
            obj[key] = value % test_case.test_data_var
            # 查找方法并执行
            res = re.findall(r"<func:(.+?)>", obj[key])
            if any(res):
                if hasattr(test_case, res[0]):
                    obj[key] = getattr(test_case, res[0])()
                else:
                    raise MethodNotFoundError(f"method: {res[0]} not found")

        elif isinstance(value, dict):
            _replace_value(value, test_case)
        elif isinstance(value, list):
            for item in value:
                _replace_value(item, test_case)
        else:
            continue


def data_provider(filename=None, stop_on_error=False):
    """
    The data provider for test method in test case
    :param filename: the test data file, default case name is script name + ".json"
    :param stop_on_error: If true, the case will stop if 1 data iteration failed.
    :return:
    """

    def outer(func):
        @wraps(func)
        def wrapper(*args):
            test_case = locals()["args"][0]
            case_file = inspect.getfile(test_case.__class__)
            if filename:
                case_file = filename
            test_data_file = case_file + ".json"
            if not os.path.exists(test_data_file):
                raise TestDataFileNotFound(f"Cannot found test data for case {test_case.__class__.__name__}")
            with open(test_data_file) as file:
                test_data = json.load(file)
            iteration = 1
            for data in test_data["data"]:
                header = data.get("header", f"Iteration {iteration}")
                try:
                    iteration += 1
                    test_case.reporter.add_step_group(header)
                    _replace_value(data, test_case)
                    func(*args, data)
                except Exception as ex:
                    if not stop_on_error:
                        test_case.reporter.add(StepResult.EXCEPTION, f"Exception on {header}")
                    else:
                        raise ex
                finally:
                    test_case.reporter.end_step_group()

        return wrapper

    return outer
