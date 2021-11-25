# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 22:25
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: manager.py


from core.config.setting import static_setting
from core.testengine.caserunner import CaseRunner
from core.testengine.testlist import TestList

runner = None


def load_settings(setting_path=None):
    """
    加载所有静态配置
    """
    if setting_path:
        static_setting.setting_path = setting_path
    static_setting.load_all()


def load_test_list(testlist):
    """
    读取测试用例并且返回测试用例对象
    """
    global runner
    test_list = TestList(testlist)
    runner.set_test_list(test_list)


def init_engine():
    """
    初始化测试引擎
    """
    global runner
    runner = CaseRunner()


def load_resource(resource_file, username):
    """
    装载测试资源
    """
    global runner
    runner.load_resource(resource_file, username)


def get_test_list():
    """
    装载测试列表
    @return:
    """
    if runner is None or not runner.test_list_ready:
        return []
    # 返回测试结果
    ret = []
    for test in runner.test_list.test_cases:
        ret.append(test)
    return ret


def run_test():
    """
    执行测试用例
    """
    global runner
    runner.start()
    runner.wait_for_test_done()
    print(runner.result_report.root.to_text())
    tp_stats = runner.result_report.root.get_test_point_stats()
    print(f"PASS: {tp_stats[0]}, FAIL: {tp_stats[1]}")
    print(f"ERROR: {tp_stats[2]}, WARNING: {tp_stats[3]}, EXCEPTION: {tp_stats[4]}")


if __name__ == "__main__":
    load_settings()
    init_engine()
    load_resource("/Users/lilen/PycharmProjects/autoframework/product/resource/code_test.json", "dechen")
    load_test_list("/Users/lilen/PycharmProjects/autoframework/product/testlist/demo_list.testlist")
    runner.start()
    runner.wait_for_test_done()
    print(runner.result_report.root.to_text())
