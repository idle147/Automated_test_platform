# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 21:32
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: reporter.py
import collections
import os
from enum import Enum, IntEnum
from functools import wraps
from threading import Event, Lock

from core.tool.time_tool import TimeTool


# =====================================
# 内容
#   1. 测试步骤和日志分离
#   2. 测试步骤的控制
#   3. 日志的分类

# 基于树形的测试步骤
#   1. 通过测试报告单例（ResultReporter）来控制整个测试用例执行周期的报告输出
#   2. 将测试结果映射成树形数据结构
# =====================================

def locker(lock):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                lock.acquire()
                return func(*args, **kwargs)
            finally:
                lock.release()

        return inner

    return outer


class NodeType(IntEnum):
    """
    表示节点类型
    """
    Step = 1
    Case = 2
    TestList = 3
    Other = 256


class StepResult(IntEnum):
    """
    表示节点状态
    """
    INFO = 1  # 表示节点的默认状态
    PASS = 2  # 表示节点通过
    FAIL = 3  # 表示测试点验证失败
    STOP = 4  # 表示测试点停止执行
    EXCEPTION = 8  # 表示执行的时候发生了未经处理的异常
    WARNING = 16
    ERROR = 32  # 表示抓住了代码的异常并进行了处理


class StepInfo(Enum):
    """
    表示步骤类别
    """
    INFO = 1


class ResultReporter:
    my_lock = Lock()

    def __init__(self, logger):
        self.root = ResultNode("Root")
        self.recent_node = self.root  # 最近节点

        # 失败回滚
        self.recent_case = None  # 当前测试用例标识符,为None表示添加失败
        self.recent_list = None  # 测试节点列表
        self.halt_on_failure = False  # 失败停止标识符
        self.halt_on_exception = False  # 异常停止标识符
        self.halt_on_stop = False  # 中止停止标识符
        self.halt_event = Event()  # 事件信号量

        self.logger = logger
        self.case_logger = None

    def search_result(self, case_name):
        """
        搜索给定的测试用例名称的测试结果
        """
        self._search_result(self.root, case_name)

    @locker(my_lock)
    def add_node(self, header, message="", status=StepResult.INFO, node_type=NodeType.Other):
        """
        添加最近节点的子节点
        """
        self.recent_node = self.recent_node.add_child(header=header,
                                                      message=message,
                                                      status=status,
                                                      node_type=node_type)

    # 若添加的节点没有子节点(如:叶子节点),则需要执行一次pop方法
    @locker(my_lock)
    def add_step_group(self, group_name):
        """
            初始化一个步骤的集合
        """
        self.add_node(header=group_name, node_type=NodeType.Step)
        self._log_info(f"[Test Step Group] {group_name}")

    @locker(my_lock)
    def end_step_group(self):
        """
            退出一个步骤的集合
        """
        self.pop()

    @locker(my_lock)
    def add(self, status: StepResult, headline, message=""):
        self.recent_node.add_child(header=headline, message=message,
                                   status=status, node_type=NodeType.Step)
        self._log_info("Step: " + headline)
        self._log_info("Message" + message)
        # 每次添加测试步骤节点时, halt_event复位
        self.halt_event.clear()
        # 判断节点的状态类型, 若失败, 则阻塞线程
        if status == StepResult.FAIL and self.halt_on_failure:
            self.halt_event.wait()
        elif status == StepResult.EXCEPTION and self.halt_on_exception:
            self.halt_event.wait()
        elif status == StepResult.STOP and self.halt_on_stop:
            self.halt_event.wait()

    @locker(my_lock)
    def pop(self):
        """
        弹出最近的节点
        # TODO: 未进行节点的资源释放
        """
        # 将当前节点的recent_node的值设置为当前节点的父节点
        if self.recent_node.parent:
            self.recent_node = self.recent_node.parent

    @locker(my_lock)
    def add_event_group(self, group_name):
        rv = self.recent_node.add_child(header=group_name, node_type=NodeType.Step)
        rv.log = self.case_logger if self.case_logger is not None else self.logger
        self._log_info(f"[Event] {group_name}")
        return rv

    @locker(my_lock)
    def add_test(self, case_name):
        """
        加入当前节点清单
        """
        self.recent_node = self.recent_node.add_child(header=case_name, node_type=NodeType.Case)
        self.recent_case = self.recent_node
        self._log_info(f"[Test Case] {case_name}")

    @locker(my_lock)
    def end_test(self):
        """
        回退到当前测试用例的父节点
        """
        if self.recent_case is None:
            return
        self.recent_node = self.recent_case.parent
        self.recent_case = None

    @locker(my_lock)
    def add_list(self, list_name):
        self.recent_node = self.recent_node.add_child(header=list_name, node_type=NodeType.TestList)
        self.recent_case = self.recent_node
        self._log_info(f"[Test list] {list_name}")

    @locker(my_lock)
    def end_list(self):
        """
        回退到当前测试列表的父节点
        """
        if self.recent_list is None:
            return
        self.recent_node = self.recent_list.parent
        self.recent_list = None

    def add_precheck_result(self, result, headline):
        pass

    def is_high_priority_passed(self, priority):
        pass

    def _search_result(self, node, case_name):
        if node.type == NodeType.Step:
            return None
        for child in node.children:
            if child.header == case_name:
                return child.status
            else:
                rv = self._search_result(child, case_name)
                if rv:
                    return rv
        else:
            return None

    def _log_info(self, message):
        if self.case_logger:
            self.case_logger.info(message)
        else:
            self.logger.info(message)


class ResultNode:
    """
    测试结果节点:
        利用树形结构进行表示
    """

    def __init__(self, header, message="", status=None, parent=None, node_type=NodeType.Other):
        """
        @param header: 简短的描述信息
        @param message: 具体的描述信息
        @param status: 节点状态
        @param parent: 父节点
        @param node_type: 节点类型
        """
        self.header = header  # 简短描述信息
        self.message = message  # 具体描述信息
        self.status = StepResult.INFO if status is None else status  # 节点状态
        self.children = []  # 节点的子节点
        self.parent = parent  # 节点的父节点
        self.type = node_type  # 节点类型
        self.timestamp = TimeTool.get_time_stamp()  # 节点创建的时间戳
        self.log = None

    def add_child(self, header, status=StepResult.INFO, message="", node_type=NodeType.Other):
        """
        添加新的子节点并返回该子节点
        """
        # 初始化节点
        new_node = ResultNode(header, message=message, parent=self, node_type=node_type)

        # 在case或step类型的节点中,只允许类型是step
        if self.type in [NodeType.Step, NodeType.Case]:
            new_node.type = NodeType.Step
        self.children.append(new_node)  # 加入子节点
        new_node.set_status(status)  # 初始化当前节点状态
        return new_node

    def add(self, status, header, message=""):
        """
        简化的add方法，提供给事件驱动使用
        """
        self.add_child(header, status, message, NodeType.Step)
        if self.log:
            self.log.info(header)

    def set_status(self, status):
        """
        设置当前节点的状态, 同时更新父节点的状态
        """
        # 不做状态设置的节点判断
        if self.type == NodeType.Other:
            return
        if status == StepResult.INFO:
            return
        # 更改当前节点的状态
        if self.status in [StepResult.INFO, StepResult.PASS]:
            self.status = status
        # 更新父节点状态
        self.parent.set_status(status)

    @property
    def is_leaf(self):
        return any(self.children)

    def to_dict(self):
        """
        将结果生成字典, 以便JSON格式输出
        @return:
        """
        ret = {"header": self.header,
               "status": self.status,
               "message": self.message,
               "type": self.type.value,
               "children": [],
               "timestamp": self.timestamp}
        # 添加子节点信息
        for child in self.children:
            ret["children"].append(child.to_dict())
        return ret

    def to_text(self, indent=0):
        """
        将结果生成文本类型的结构, 以便转换成格式化文本信息
        @param indent: 缩进层次
        @return:
        """
        # 添加初始信息, 缩进层次和时间戳
        ret = f"{self._get_intent(indent)}[{self.timestamp}]"

        # 添加测试用例类别信息
        if self.type == NodeType.Case:
            ret += "[TestCase]"
        if self.type == NodeType.TestList:
            ret += "[TestList]"
        ret += self.header

        # 添加节点信息
        if self.type in [NodeType.Case, NodeType.Step]:
            ret += self._get_dot_line(ret, 120)
            ret += self.status.name
        ret += os.linesep  # 给出当前平台上的终止符, 例如，Windows使用’\r\n’，Linux使用’\n’而Mac使用’\r’。

        # 添加详细信息
        if self.message:
            ret += self._get_intent(indent)
            ret += f"描述: {self.message}{os.linesep}"

        # 添加子节点信息
        for child in self.children:
            ret += child.to_text(indent + 1)

        return ret

    @staticmethod
    def _get_dot_line(line, line_max):
        if len(line) >= line_max:
            return line
        else:
            return "-" * (line_max - len(line))

    @staticmethod
    def _get_intent(indent):
        """
        添加缩进层次
        @param indent:缩进层次
        @return:
        """
        return "+" * (indent * 2)

    # =====================================
    # 测试结果的统计方法
    # 1. 基于测试用例的统计，统计数量相对稳定，因为执行的测试用例数量是一定的，
    #    但是这种方法就要求测试用例的设计颗粒度足够细。
    #    如果颗粒度太粗，比如一个测试用例包括了太多的测试点，任何一个不严重的测试点失败，都会导致整个测试用例的失败
    # =====================================
    def get_test_case_stats(self):
        """
        根据当前的结果, 将相应的统计值置为 1 并返回;
        否则,遍历自己的children属性,递归调用get_test_case_stats
        """
        stats = collections.Counter({
            "stats_pass": 0,
            "stats_fail": 0,
            "stats_error": 0,
            "stats_warning": 0,
            "stats_exception": 0
        })
        if self.type == NodeType.Case:
            self.stats_judge(stats)
        else:
            for child in self.children:
                child_stats = child.get_test_case_stats()
                stats.update(child_stats)
        return stats

    # =====================================
    # 2. 基于测试点的统计，能够解决测试用例颗粒度的问题，不管测试用例如何设计，整个统计过程不会关心有多少测试用例。
    #    但是由于在测试过程中，测试点的执行不一定是固定的
    #    比如一个测试点的失败会导致之后的测试点无法执行，从而使这些测试点无法被统计到，
    #    所以使用这种方法在统计通过率的时候，分母是不确定的。
    # =====================================
    def get_test_point_stats(self):
        stats = collections.Counter({
            "stats_pass": 0,
            "stats_fail": 0,
            "stats_error": 0,
            "stats_warning": 0,
            "stats_exception": 0
        })
        for child in self.children:
            child_stats = child.get_test_point_stats()
            stats.update(child_stats)
        # 递归至只有到了叶节点,才能返回这个节点的状态
        # 因为叶子节点的状态会影响所有父节点的状态
        if not self.is_leaf:
            self.stats_judge(stats)
        return stats

    def stats_judge(self, stats):
        if self.status == StepResult.PASS:
            stats["stats_pass"] = 1
        elif self.status == StepResult.FAIL:
            stats["stats_fail"] = 1
        elif self.status == StepResult.ERROR:
            stats["stats_error"] = 1
        elif self.status == StepResult.WARNING:
            stats["stats_warning"] = 1
        elif self.status == StepResult.EXCEPTION:
            stats["stats_exception"] = 1


if __name__ == '__main__':
    import logging

    rr = ResultReporter(logging)
    # 添加一个测试列表节点
    rr.add_list("Test List 1")

    # 添加一个测试用例节点
    rr.add_test("Test Case 1")

    # 添加一个SETUP步骤节点
    rr.add_step_group("SETUP")
    # 添加一些步骤
    rr.add(StepResult.PASS, "Do Something Setup", "I'm doing something")
    rr.end_step_group()

    # 添加一个测试步骤节点
    rr.add_step_group("TEST")
    rr.add_step_group("Login to website")
    rr.add(StepResult.PASS, "Input Username", "Username is admin")
    rr.add(StepResult.PASS, "Input Password", "Password is admin")
    rr.add(StepResult.FAIL, "Login", "Login is failed")
    rr.end_step_group()

    # 这里我们少了一个end_group, 但是end_test会把我们带回正确的位置。
    rr.end_test()

    # 第二个测试用例
    rr.add_test("Test Case 2")
    rr.add_step_group("SETUP")
    rr.add(StepResult.PASS, "Do Something Setup", "I'm doing something")
    rr.end_step_group()

    rr.add_step_group("TEST")
    rr.add_step_group("Login to website")
    rr.add(StepResult.PASS, "Input Username", "Username is admin")
    rr.add(StepResult.PASS, "Input Password", "Password is admin")
    rr.end_step_group()
    rr.end_test()
    rr.add_list("Sub Test List")
    rr.add_test("Test Case 3")
    rr.add_step_group("SETUP")
    rr.add(StepResult.PASS, "Do Something Setup", "I'm doing something")
    rr.end_step_group()

    rr.add_step_group("TEST")
    rr.add_step_group("Login to website")
    rr.add(StepResult.PASS, "Input Username", "Username is admin")
    rr.add(StepResult.PASS, "Input Password", "Password is admin")
    rr.end_step_group()
    rr.end_test()
    rr.end_list()

    rr.add_test("Test Case 4")
    rr.add_step_group("SETUP")
    rr.add(StepResult.PASS, "Do Something Setup", "I'm doing something")
    rr.end_step_group()

    rr.add_step_group("TEST")
    rr.add_step_group("Login to website")
    rr.add(StepResult.PASS, "Input Username", "Username is admin")
    rr.add(StepResult.PASS, "Input Password", "Password is admin")
    rr.end_step_group()
    rr.end_test()

    rr.end_list()

    print(rr.root.to_text())
    tp_stats = rr.root.get_test_point_stats()
    print(f"PASS: {tp_stats[0]}, FAIL: {tp_stats[1]}")
    print(f"ERROR: {tp_stats[2]}, WARNING: {tp_stats[3]}, EXCEPTION: {tp_stats[4]}")
    tc_stats = rr.root.get_test_case_stats()
    print(f"PASS: {tc_stats[0]}, FAIL: {tc_stats[1]}")
    print(f"ERROR: {tc_stats[2]}, WARNING: {tc_stats[3]}, EXCEPTION: {tc_stats[4]}")

    # import json
    # print(json.dumps(rr.root.to_dict(), indent=4))
