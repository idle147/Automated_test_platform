# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 22:40
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: runner.py

import os

from flask import make_response, jsonify
from flask_restplus import Namespace, reqparse, Resource

from controller.manager import *

"""
    API实现: 继承RESTPlus中的Resource
    API组成: namespace(命名空间)
            Route(注册每个API的URI路径)
    API请求: 实现相应的HTTP中定义METHOD名字的方法
"""

# 设置命名空间
name_space = Namespace("case-runner", description="Case Runner")

runner_param = reqparse.RequestParser()
runner_param.add_argument("status", required=True, type=str, location="json")
runner_param.add_argument("setting_path", required=False, type=str, location="json")

test_list_param = reqparse.RequestParser()
test_list_param.add_argument("file", required=True, type=str, location="json")

resource_param = reqparse.RequestParser()
resource_param.add_argument("file", required=True, type=str, location="json")
resource_param.add_argument("user", required=True, type=str, location="json")


def _get_response(result, message, code):
    return make_response(jsonify({"Result": result, "Message": message}), code)


# 通过命名空间实例的route来注册每个API本身的URI路径
@name_space.route("")  # 路径为/case-runner
class CaseRunnerApi(Resource):
    """
    代表了测试执行的api
    """

    @name_space.expect(runner_param)  # 异常处理装饰器
    @name_space.response(202, "Case Start Running")
    @name_space.response(400, "Wrong Parameters")
    def put(self):
        arg = runner_param.parse_args()
        if arg['status'].lower() == "start":
            run_test()
            return _get_response(True, "Test Started", 202)
        elif arg['status'].lower() == "init":
            init_engine()
            load_settings(arg['setting_path'])
            return _get_response(True, "Test Runner Initialized", 200)
        else:
            return _get_response(False, "Unknown Status", 400)


@name_space.route("/testlist")
class TestListApi(Resource):  # 路径为"/case-runner/testlist"
    """
        实现测试结果的动态获取、静态配置的设置和保存
    """
    @name_space.response(200, "Load Test List")
    @name_space.response(400, "Wrong Parameters")
    @name_space.response(500, "Error")
    @name_space.expect(test_list_param)
    def put(self):
        arg = test_list_param.parse_args()
        if not os.path.exists(arg['file']):
            return _get_response(False, "Test List not found", 500)
        try:
            load_test_list(arg['file'])
            return _get_response(True, "Test List loaded", 200)
        except Exception as ex:
            return _get_response(False, str(ex), 500)

    @name_space.response(200, "Test List")
    @name_space.response(500, "Error")
    def get(self):
        return make_response(jsonify(get_test_list()), 200)


@name_space.route("/resource")
class TestResourceApi(Resource):  # 路径为"/case-runner/resource"

    @name_space.response(200, "Test Resource Loaded")
    @name_space.response(400, "Wrong Parameters")
    @name_space.response(500, "Error")
    @name_space.expect(resource_param)
    def put(self):
        arg = resource_param.parse_args()
        if not os.path.exists(arg['file']):
            return _get_response(False, "Resource File", 500)
        try:
            load_resource(arg['file'], arg["user"])
            return _get_response(True, "Test Resource loaded", 200)
        except Exception as ex:
            return _get_response(False, str(ex), 500)
