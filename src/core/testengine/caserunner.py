# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 9:45
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: caserunner.py

"""
Test Engine
"""

# =====================================
# 一个好的测试引擎:
#   1. 希望测试用例能够实时输出正在执行的步骤
#   2. 测试用例执行失败时,可以挂起测试
#   3. 收集和分析测试用例

# 测试引擎的模块:
#   1. 配置装载
#   2. 测试资源装载
#   3. 测试列表装载
#   4. 测试用例生命周期管理和执行

# 时序说明:
#   1. 导入测试用例
#   2. 收集测试资源池的资源并判断当前的资源是否满足测试需要(根据测试用例中的资源需求)
#   3. 加载配置文件,执行测试用例,管理执行过程
#   4. 生成测试结果和日志
#
# 测试引擎工作
#   1. 实例化所有继承了TestCaseBase配置类 的测试用例类
#   2. 根据配置的文件路径, 读取配置信息
#   3. 动态赋值给测试用例的setting字段
#
# 测试引擎执行测试用例的最小单位是 测试列表
# =====================================
import importlib
import os
import threading
from enum import Enum

from core.case.base import TestCaseBase
from core.case.precondition import IsTestCaseType, IsTestCasePriority, IsPreCasePassed, IsHigherPriorityPassed
from core.config.logic_module import ModuleManager, ModuleType
from core.config.setting import static_setting, SettingBase
from core.resource.error import ResourceNotMeetConstraintError, ResourceLoadError, ResourceNotRelease
from core.resource.pool import ResourcePool
from core.result.logger import logger
from core.result.reporter import ResultReporter, StepResult
from core.testengine.testlist import TestList
from core.tool.time_tool import TimeTool


@static_setting.setting("CaseRunner")
class CaseRunnerSetting(SettingBase):
    """
    The case runner setting
    """
    dir_path = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    default_case_setting_path = os.path.join(dir_path, "settings", "test_settings")  # 默认的测试用例存放路径
    log_path = os.path.join(dir_path, "log", "ats_logs")  # 一般log日志输出目录
    case_log = os.path.join(dir_path, "log", "case_logs")  # 测试用例输出的日志存放的路径
    log_level = "INFO"


class CaseImportError(Exception):
    def __init__(self, msg, inner_ex=None):
        super().__init__(msg)
        self.inner_ex = inner_ex


class TestEngineNotReadyError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class RunningStatus(Enum):
    Idle = 1  # 挂起
    Running = 3  # 运行


class CaseRunner:
    """
    测试用例执行器
    """

    def __init__(self):
        self.status = RunningStatus.Idle
        self.resource_pool = None
        self.list_setting = None
        self.test_list = None
        self.running_thread = None
        self.case_tree = {}
        self.priority_list = []
        self.pre_conditions = []
        self.module_manager = ModuleManager()

        self.logger = logger.register("CaseRunner", filename=os.path.join(CaseRunnerSetting.log_path, "CaseRunner.log"),
                                      default_level=CaseRunnerSetting.log_level)
        self.result_report = ResultReporter(self.logger)  # 将logger实例共享给ResultReporter
        self.logger.info("执行器装载完毕")

        self.case_log_folder = None
        self.case_result = dict()

    def load_resource(self, file_name, username):
        """
        装载测试资源
        @param file_name: 资源文件名
        @param username:  用户名
        @return:
        """
        self.resource_pool = ResourcePool()
        try:
            self.resource_pool.load(file_name, username)
            for key, device in self.resource_pool.topology.items():
                # 如果需要预连接, 获取管理实例对其进行连接
                if device.pre_connect:
                    device_instance = device.get_comm_instance()
                    if hasattr(device_instance, "connect"):
                        device_instance.connect()
        except ResourceLoadError as rle:
            # 资源文件读取错误
            self.logger.exception(rle)
            self.resource_pool = None
        except ResourceNotRelease as rnr:
            # 资源文件被占用,未释放
            self.logger.exception(rnr)
            self.resource_pool = None
        except Exception as ex:
            self.logger.exception(ex)
            self.resource_pool = None
        self.logger.info("测试资源装载完毕")

    @property
    def resource_ready(self):
        """
        判断测试资源是否已经准备完毕
        @return:
        """
        return self.resource_pool is not None

    @property
    def test_list_ready(self):
        """
        判断测试列表是否被装载
        @return:
        """
        return self.test_list is not None

    def load_test(self, test_name) -> TestCaseBase:
        """
        动态实例化测试用例
        """
        # 获取测试用例的模块名和类名
        case_module_name = ".".join(test_name.split(".")[0: -1])
        case_name = test_name.split(".")[-1]
        # 动态引用测试用例
        try:
            case_module = importlib.import_module(case_module_name)
            return getattr(case_module, case_name)(self.result_report)
        except Exception as ex:
            # 导入测试用例失败，抛出异常
            raise CaseImportError("导入测试用例 [%s] [失败]!" % test_name, ex)

    def set_test_list(self, test_list: TestList):
        """
        装载测试列表
        """
        self.test_list = test_list
        # 清除当前测试列表
        self.list_setting = None
        self.case_tree.clear()
        # 载入测试列表
        self._import_list_case(self.case_tree, self.test_list)
        # 判断该列表是否需要有优先级需求
        if any(self.test_list.setting.priority_to_run):
            self.priority_list = self.test_list.setting.priority_to_run
        self.logger.info("测试列表装载完毕")

    def start(self):
        """
        测试引擎开始执行
        """
        # 检查 配置、资源、和测试列表
        if self.status == RunningStatus.Running:
            return
        if not self.resource_ready:
            raise TestEngineNotReadyError("测试引擎未准备就绪，【测试资源】未装载")
        if self.test_list is None:
            raise TestEngineNotReadyError("测试引擎未准备就绪，【测试列表】未装载")

        # 初始化操作
        self.status = RunningStatus.Running
        self.case_log_folder = os.path.join(CaseRunnerSetting.case_log, TimeTool.get_time_stamp())
        self.running_thread = threading.Thread(target=self.__main_test_thread)
        self.running_thread.start()

    def wait_for_test_done(self):
        self.running_thread.join()

    # =====================================
    # 测试用例流程控制
    #   开始 -> 前置条件判断 -> 逻辑模块装载 -> 获取资源 -> setup -> code_test -> cleanup -> 测试用例执行结束
    # =====================================
    def run_case_lcm(self, test: TestCaseBase):
        """
        执行测试用例生命周期管理
        这个方法应该在子线程被运行
        """
        self.__init_precondition(test)
        # 判断前置条件是否全部通过
        if not self.__pre_check(test):
            return
        # 逻辑模块的装载执行和测试用例执行
        self.module_manager.run_module(ModuleType.PRE)  # 预装载
        self.module_manager.run_module(ModuleType.PARALLEL)  # 并行执行
        self.__run_case(test)  # 运行模块,执行单个测试用例
        self.module_manager.stop_module()  # 停止模块
        self.module_manager.run_module(ModuleType.POST)  # 执行后置模块

    def _import_list_case(self, case_tree_node, test_list, log_path=None):
        """
        递归导入测试列表中的测试用例
        @param case_tree_node:构建测试列表和测试用例的信息
        @oarm test_list: 测试列表
        """
        # 测试日志文件路径载入
        case_log_path = test_list.test_list_name
        if log_path:
            case_log_path = os.path.join(log_path, case_log_path)

        # 构建测试列表和测试用例的信息
        case_tree_node["list_name"] = test_list.test_list_name
        case_tree_node["test_cases"] = list()
        case_tree_node['sub_list'] = []

        # 遍历测试列表中的测试用例, 并加入测试用例树
        for testcase in test_list.test_cases:
            if testcase.strip() == "":  # 去除空格后, 没有字符串, 则遍历下一个
                continue
            # 规定每条测试用例用 逗号 来分割测试用例的[包路径名]和[配置文件名]
            case_entry = testcase.split(",")
            case_name = case_entry[0]
            case_setting_file = ""
            if len(case_entry) > 1:
                case_setting_file = case_entry[1]
            # 导入测试用例
            case_descriptor = {}
            try:
                # 初始化
                case_descriptor['case'] = self.load_test(case_name)
                case_descriptor['case_name'] = case_name.split(".")[-1]
                case_descriptor['log_path'] = case_log_path
                case_descriptor['setting_file'] = case_setting_file
                # 设置测试用例配置文件路径
                if test_list.setting.case_setting_path:
                    case_descriptor['setting_path'] = test_list.setting.case_setting_path
                else:
                    case_descriptor['setting_path'] = CaseRunnerSetting.default_case_setting_path
                # 设置当前测试用例的优先级,并加入优先级清单中, 默认设置为 999(最高)
                case_priority = getattr(case_descriptor['case'], "priority", 999)
                if case_priority not in self.priority_list:
                    self.priority_list.append(case_priority)
            except CaseImportError as cie:
                # 测试用例导入失败
                self.logger.error(f"不能导入测试用例{case_name}")
                self.logger.exception(cie)
            # 加入测试用例树
            case_tree_node['test_cases'].append(case_descriptor)

        # 遍历测试列表中的子测试列表, 并加入测试用例树
        for sub_list in test_list.sub_list:
            sub_list_dict = {}
            case_tree_node['sub_list'].append(sub_list_dict)
            # 递归调用
            self._import_list_case(sub_list_dict, sub_list, log_path=case_log_path)

    # =====================================
    # 前置条件判断:
    #   针对每个测试用例创建前置条件, 配置不同, 前置条件不同
    # =====================================
    def __init_precondition(self, test: TestCaseBase):
        # 实现前置条件判断
        self.pre_conditions.clear()
        # 判断是否是指定类型
        self.pre_conditions.append(IsTestCaseType(self.test_list.setting.run_type))
        # 判断是否是指定优先级
        if any(self.test_list.setting.priority_to_run):
            self.pre_conditions.append(IsTestCasePriority(self.test_list.setting.priority_to_run))
        # 判断是否是某个期望的结果
        if any(test.pre_tests):
            self.pre_conditions.append(IsPreCasePassed(self.case_result))
        # 判断高优先级测试用例是否全部通过
        self.pre_conditions.append(IsHigherPriorityPassed(test.priority, self.case_result))

    def __pre_check(self, test: TestCaseBase):
        """
        运行所有检查前置条件的实例化对象, 并检查前置条件是否全部执行通过
        @param test:
        @return:
        """
        for condition in self.pre_conditions:
            if not condition.is_meet(test, self.result_report):
                self.result_report.add(StepResult.INFO, f"{test.__class__.__name__}不能执行！")
                return False
        return True

    def __get_case_log(self, path, case_name):
        """
        为每一个注册用例注册一个日志实例, 输出到相应的测试用例目录中
        @param path:
        @param case_name:
        @return:
        """
        log_path = os.path.join(self.case_log_folder, path, f"{case_name}.log")
        return logger.register(case_name, filename=log_path, is_test=True)

    def __main_test_thread(self):
        try:
            self.__run_test_list(self.case_tree)
        finally:
            self.status = RunningStatus.Idle

    def __run_test_list(self, testlist):
        """
        递归执行子测试列表
        @param testlist:
        @return:
        """
        self.result_report.add_list(testlist['list_name'])

        # 执行子测试用例
        for test in testlist['test_cases']:
            test["case"].get_setting(test["setting_path"], test["setting_file"])
            # 为每个测试用例注册一个日志实例, 输出到相应的测试用例目录中
            self.result_report.case_logger = self.__get_case_log(test['log_path'], test['case_name'])
            # 测试结果初始化
            self.case_result[test["case_name"]] = dict()
            self.case_result[test["case_name"]]['priority'] = test["case"].priority
            self.case_result[test["case_name"]]['result'] = False
            # 执行测试用例生命周期管理
            self.run_case_lcm(test['case'])
            self.result_report.case_logger = None
            # 释放用例的日志文件
            logger.unregister(test['case_name'])

        # 递归调用子测试用例
        for test_list in testlist['sub_list']:
            self.__run_test_list(test_list)

        self.result_report.end_list()

    def __run_case(self, test: TestCaseBase):
        """
        测试用例执行线程
        """
        self.result_report.add_test(test.__class__.__name__)
        _continue = True

        # 收集资源, 资源收集失败则返回
        try:
            self.result_report.add_step_group("收集测试资源")
            test.collect_resource(self.resource_pool)
        except ResourceNotMeetConstraintError as rnmce:
            self.result_report.add(StepResult.EXCEPTION, "测试资源不满足条件", str(rnmce))
            _continue = False
        except Exception as e:
            self.result_report.add(StepResult.EXCEPTION, "捕获异常！", str(e))
            _continue = False
        finally:
            self.result_report.end_step_group()
        if not _continue:
            self.result_report.end_test()
            return
        # 执行SETUP
        try:
            self.result_report.add_step_group("SETUP")
            test.setup()
            self.result_report.end_step_group()
        except Exception as e:
            self.result_report.add(StepResult.EXCEPTION, "捕获异常!", str(e))
            self.result_report.end_step_group()
            self.__call_cleanup(test)
            return
        # 执行TEST
        try:
            self.result_report.add_step_group("TEST")
            test.test()
            self.result_report.end_step_group()
        except Exception as e:
            self.result_report.add(StepResult.EXCEPTION, "捕获异常!", str(e))
            self.result_report.end_step_group()
            self.__call_cleanup(test)
            return
        # 执行CLEANUP
        self.__call_cleanup(test)

    def __call_cleanup(self, test: TestCaseBase):
        """
        执行清除操作
        """
        try:
            self.result_report.add(StepResult.INFO, "CLEANUP")
            test.cleanup()
        except Exception as e:
            self.result_report.add(StepResult.EXCEPTION, "EXCEPTION!", str(e))
        finally:
            self.result_report.pop()
            self.case_result[test.__class__.__name__]['result'] = \
                self.result_report.recent_case.status == StepResult.PASS
            self.result_report.end_test()
