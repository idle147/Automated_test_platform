# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 22:48
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: index.py

"""
    定义Flask服务器
"""

from flask import Flask, Blueprint
from flask_restplus import Api

from user_interface.rest.endpoint.runner import name_space

app = Flask(__name__)  # 实例化Flask对象
api = Api(title="Automation Test Platfrom API", version="1.0")  # 新建一个RESTPlus的API对象

# 初始化blueprint对象(可以生成Swagger风格的API文档页面)
bp = Blueprint("api", __name__, url_prefix="/rest")
api.init_app(bp)

# 添加命名空间实例
api.add_namespace(name_space)

# 注册Blueprint对象
app.register_blueprint(bp)

app.run(host="0.0.0.0", port=5000)
