# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 22:58
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: manager.py

import ast
import json
import os
# =====================================
# 用例管理器: 动态引用测试用例 和 抽象代码树
#   1. 发现测试用例
#   2. 管理测试用例(测试用例合法性验证, 前端展示, 放入测试列表)
# =====================================
from importlib import import_module

"""
    自动发现测试用例: 动态引用 & 静态扫描
"""


# =====================================
# 动态引用测试用例
#   1. 提供测试用例所在的根目录, 将其作为测试用例包的路径
#   2. 通过importlib提供的import_module方法实现动态引用
#     2.1 当发现引用的包是一个文件夹时, 遍历文件夹中的所有内容
#         对于子文件夹,则继续通过动态引用递归查找
#     2.2 如果发现引用的包是python文件, 则尝试引用并查找该文件是否包含父类是TestCaseBase类的类
# =====================================
def load_cases(package, case_tree):
    """
    读取测试用例信息的方法
    :param package: 测试用例所在的根目录
    :param case_tree: 字典, 模块被引用后产生的对象包含__spec__属性
    :return:
    """
    # 这个包是一个文件夹，我们才继续查找其所包含的文件
    module = import_module(package)

    # origin保存了该模块文件的路径
    if module.__spec__.origin is None:
        return

    # 如果是一个目录,则包含__init__.py文件
    if os.path.basename(module.__spec__.origin) == "__init__.py":
        case_tree["sub_module"] = []
        case_tree["cases"] = []
        module_path = os.path.dirname(module.__spec__.origin)
        for file in os.listdir(module_path):
            if file == "__pycache__":
                continue
            if os.path.isdir(os.path.join(module_path, file)):
                # 如果是一个子文件夹，则代表可能是一个子包，递归查找
                sub_module = {"module": f"{package}.{file}"}
                case_tree["sub_module"].append(sub_module)
                load_cases(f"{package}.{file}", sub_module)
            elif os.path.splitext(file)[1] == ".py":
                case_module_name = f"{package}.{os.path.splitext(file)[0]}"
                try:
                    # 测试用例如果有语法错误会导致导入异常，需要catch
                    case_module = import_module(case_module_name)
                except:
                    continue
                for k, v in case_module.__dict__.items():
                    if hasattr(v, "__base__") and v.__base__.__name__ == "TestCaseBase":
                        case_info = {'name': f"{case_module_name}.{v.__name__}"}
                        get_case_info(v, case_info)
                        case_tree["cases"].append(case_info)


def get_case_info(case, case_info):
    """
    获取测试用例类的具体信息
    @param case:
    @param case_info:
    @return:
    """
    case_info['priority'] = getattr(case, "priority", 999)
    case_info['test_type'] = getattr(case, "test_type", "")
    case_info['feature_name'] = getattr(case, "feature_name", "")
    case_info['testcase_id'] = getattr(case, "testcase_id", "")
    case_info['pre_tests'] = getattr(case, "pre_tests", [])
    case_info['skip_if_high_priority_failed'] = getattr(case, "skip_if_high_priority_failed", False)
    case_info['doc'] = getattr(case, "__doc__", "")


# =====================================
# 抽象代码树AST
#   1. 给出测试用例所在的根目录
#   2. 通过文件遍历的方法,寻找所有的python文件进行编译
#   3. 查找代码树中类定义的AST对象ClassDef, 并判断其属性中是否包含TestCaseBase
#   4. 再根据decorator_list中的case装饰器的属性,获取相应的测试用例信息
# =====================================
def load_case_ast(path, case_tree, base_path):
    """
    利用AST获取测试用例
    :param path: 测试用例的绝对路径
    :param case_tree: case tree dict() object
    :param base_path: The base path of the test case
    :return:
    """
    case_tree["cases"] = []
    case_tree["sub_modules"] = []
    for file in os.listdir(path):
        if file == "__pycache__":
            continue
        if os.path.isdir(os.path.join(path, file)):
            sub_module = {"name": path.replace("/", ".").replace("\\", ".") + "." + file}
            sub_module["name"] = sub_module["name"][len(base_path):]
            case_tree["sub_modules"].append(sub_module)
            load_case_ast(os.path.join(path, file), sub_module, base_path)
        elif os.path.splitext(file)[1] == ".py":
            case_file_name = os.path.join(path, file)
            case_moudule_name = os.path.splitext(case_file_name)[0].replace("/", ".").replace("\\", ".")
            case_moudule_name = case_moudule_name[len(base_path):]
            with open(case_file_name) as case_file:
                file_ast = ast.parse(case_file.read())
            if file_ast:
                for ast_obj in file_ast.body:
                    if isinstance(ast_obj, ast.ClassDef) and hasattr(ast_obj, "bases"):
                        for base_cls in ast_obj.bases:
                            if base_cls.id == "TestCaseBase":
                                case_info = {"name": f"{case_moudule_name}.{ast_obj.name}"}
                                get_ast_case_info(ast_obj, case_info)
                                case_tree['cases'].append(case_info)


def get_ast_case_info(case, case_info):
    case_info['priority'] = 999
    case_info['test_type'] = ""
    case_info['feature_name'] = ""
    case_info['testcase_id'] = ""
    case_info['pre_tests'] = ""
    case_info['skip_if_high_priority_failed'] = ""
    case_info['doc'] = ""
    for decorator in case.decorator_list:
        if decorator.func.id == "case":
            for keyword in decorator.keywords:
                case_info[keyword.arg] = getattr(keyword.value, keyword.value._fields[0], None)

    if isinstance(case.body[0], ast.Expr):
        case_info['doc'] = getattr(case.body[0].value, case.body[0].value._fields[0], "")


if __name__ == '__main__':
    cases = {"module": "product.testcase"}
    load_case_ast("/Users/lilen/PycharmProjects/autoframework/product/testcase",
                  cases, "/Users/lilen/PycharmProjects/autoframework/")
    print(json.dumps(cases, indent=2))
