# -*- coding:utf-8 -*-
# @Time: 2021/11/21 0021 18:18
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: logger.py

import logging
import logging.handlers
import os
import time

from core.tool.file_tool import FileTool

logger_level = {
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "DEBUG": logging.DEBUG,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class LoggerManager:

    def __init__(self):
        # 用于记录logger的配置信息
        self.logger_info = {}

    def register(self, logger_name, file_path=None, console=True,
                 default_level=logging.INFO, **kwargs):
        """
        注册logger
        @param logger_name: 日志实例的名称, 唯一表示
        @param file_path: 文件路径, 必须是一个绝对路径或者相对路径,而不能是单独的文件名
        @param console: 是否输出到控制台
        @param default_level: 默认输出等价
        @param kwargs: 其他参数
        @return:
        """

        # 基本参数设置
        file_size_limit = kwargs.get("size_limit", 1024 * 1024)  # 单个文件大小，默认一个文件大小为1M
        max_files = kwargs.get("max_files", None)  # 最大文件数
        file_mode = kwargs.get("mode", "w")  # 日志产生模式, 追加还是新建

        """
            for_test: 表示注册的模块需要在测试用例执行期间， 同时向测试用例所在的日志目录输出日志信息
            is_test: 表示该日志是一个测试用例日志
            当我们注册一个新的测试用例的日志输出时, 所有相关的其他模块的日志都会向测试用例目录输出测试用例执行期间所产生的日志
        """
        for_test = kwargs.get("for_test", False)  # 日志对测试用例开放
        is_test = kwargs.get("is_test", False)  # 日志是测试用例日志

        log_format = kwargs.get("format", None)  # 日志条目的输出格式
        zip_logger = kwargs.get("zip", False)  # 是否压缩日志标识符
        if log_format is None:
            log_format = "[%(asctime)s][%(name)s]-<thread:%(thread)s>-(line:%(lineno)s), [%(levelname)s]: %(message)s"

        # 获取新的logger实例
        logger = logging.getLogger(logger_name)
        self.logger_info[logger_name] = {}
        self.logger_info[logger_name].update({
            'timestamp': time.localtime(),
            'for_test': for_test,
            'is_test': is_test
        })

        # 指定了存放日志的文件路径
        if file_path:
            FileTool.check_and_create_directory(file_path)
            self.logger_info[logger_name].update({
                'file_path': os.path.dirname(file_path),
                'file_name': os.path.basename(file_path),
                'zip': zip_logger
            })

            # 日志文件句柄的定义
            if max_files:
                file_handler = logging.handlers.RotatingFileHandler(
                    filename=file_path,
                    mode=file_mode,
                    maxBytes=file_size_limit,  # 将文件按照最大大小进行分割
                    backupCount=max_files)  # 实现日志文件自动备份
            else:
                file_handler = logging.FileHandler(file_path, mode=file_mode)  # 按照指定格式，获取日志文件流句柄

            file_handler.setFormatter(logging.Formatter(fmt=log_format))
            logger.addHandler(file_handler)

            if is_test:
                for l_logger, l_value in self.logger_info.items():
                    # 需要是一个注册了日志文件的模块才能向测试用例输出日志
                    if l_value['for_test'] and "file_name" in l_value:
                        logger_filename = os.path.join(
                            os.path.dirname(file_path), f"{l_logger}.log")
                        # 为该日志添加一个新的FileHandler来输出该模块的日志到测试用例日志所在的目录
                        case_handler = logging.FileHandler(logger_filename, mode="w")
                        case_handler.setFormatter(logging.Formatter(fmt=log_format))
                        l_value['case_handler'] = case_handler
                        l_value['logger'].addHandler(case_handler)

        # 指定了需要同步输出控制台
        if console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(fmt=log_format))
            logger.addHandler(stream_handler)

        logger.setLevel(default_level)  # 设置日志等级
        self.logger_info[logger_name]['logger'] = logger  # 设置日志的实例化对象
        return logger

    def unregister(self, logger_name):
        """
        删除注册的logger，同时将需要打包的logger文件打包
        """
        logger_dict = logging.Logger.manager.loggerDict
        if logger_name in logger_dict:
            # logging对象内移除该对象
            logger_dict.pop(logger_name)
            # 如果该日志注册了测试用例的handler，则移除
            if self.logger_info[logger_name]['is_test']:
                for _, lvalue in self.logger_info.items():
                    if 'case_handler' in lvalue:
                        lvalue['logger'].removeHandler(lvalue['case_handler'])
                        lvalue.pop("case_handler")  # 删除对应的测试用例句柄的字典信息
            self._achieve_files(logger_name)  # 将日志压缩,减少体积大小
            self.logger_info.pop(logger_name)  # 删除相应的logger_name的字典信息

    def _achieve_files(self, logger_name):
        if self.logger_info[logger_name]['zip']:
            current = time.localtime()
            output_file = "achieved_logs_%d_%d_%d_%d_%d_%d.zip" % (
                current.tm_year, current.tm_mon, current.tm_mday,
                current.tm_hour, current.tm_min, current.tm_sec
            )
            FileTool.zip_directory(
                self.logger_info[logger_name]['file_path'],
                os.path.join(self.logger_info[logger_name]['file_path'], output_file))

    def get_logger(self, logger_name):
        """
        提供给开发者获取已经注册的logger实例
        @param logger_name:
        @return:
        """
        if logger_name in self.logger_info:
            return self.logger_info[logger_name]["logger"]
        raise NameError(f"No log named {logger_name}")


# 生成日志管理者
logger = LoggerManager()

if __name__ == "__main__":
    # 路径定义
    dir_path = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    log_file_path = os.path.join(dir_path, "log")

    # =====================================
    # 不建议测试用例开发者自己生成日志实例, 而是通过测试用例执行模块来帮助生成。
    # 并将日志实例注入测试用例实例中(复用用例存放路径)
    # 这样测试用例开发者便无需关注日志存放的位置
    # =====================================
    # 注册日志
    log1 = logger.register(r"Module", os.path.join(log_file_path, "log_test", "test1.log"),
                           for_test=True, zip=False)
    case_logger = logger.register("Test_Case", os.path.join(log_file_path, "test_case", "democase.log"),
                                  is_test=True, zip=False)

    # 写入日志
    case_logger.info("This is from Test log")
    log1.info("This is from Module Log")  # 该日志会同时向log_test和test_case两个目录输出信息

    # 删除日志
    logger.unregister("Test_Case")
