import time

import core.utilities.codedom as codedom
from .openapi import SwaggerLoader

"""
    通过中间对象来生成最终的封装代码
        1. 生成Schema的封装对象
        2. 生成相应的API的调用过程 
"""

_SCHEMA_BASE = [".schemabase", "SchemaBase"]
_COMMON = [".common", ['ApiTestResult, ApiTestHelper']]
_CASE_BASE = [".casebase", "ApiTestBase"]
_TOOL_PACKAGE = "product.common.tools.casegen"
SETTING = None

repo_desc = """
    This file is auto generated by the case auto generator
    Swagger File: %(swagger_file)s
    Description: The Object Report for the API Definition
    API Doc Version: %(doc_version)s
    Date: %(gen_date)s,
"""


class ObjectCreator:
    """
        表示生成器的基类, 在初始化的时候将SwaggerLoader对象作为参数赋值给swagger属性
    """

    def __init__(self, swagger: SwaggerLoader):
        self.swagger = swagger
        self.code_statements = list()  # 用来保存生成的Code DOM语句

    def generate(self):
        """
        生成一些公共代码
            1. 生成SchemaBase的import语句
            2. 遍历SwaggerLoader实例的schema_data属性中的schema对象
            3. 每个对象由get_class方法生成
            4. 将生成的statement对象实例添加到code_statements属性中
        """
        info = {
            "swagger_file": self.swagger.main_file,
            "doc_version": self.swagger.description_data[self.swagger.main_file]['info']['version'],
            "gen_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # description
        script_doc = codedom.DocStatement(lines=[repo_desc % info])
        self.code_statements.append(script_doc)