# -*- coding:utf-8 -*-
# @Time: 2021/11/22 0022 22:28
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: start.py

import argparse
import os
import sys

from controller.manager import *

package_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(package_path, ".."))

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--setting", type=str, dest="setting",
                    help="平台静态配置路径", required=True)
parser.add_argument("-t", "--testlist", type=str, dest="testlist",
                    help="测试用例列表文件", required=True)
parser.add_argument("-r", "--resource", type=str, dest="resource",
                    help="测试资源文件", required=True)
parser.add_argument("-u", "--user", type=str, dest="user",
                    help="当前测试用户", required=True)

args = parser.parse_args()

load_settings(args.setting)
init_engine()
load_resource(args.resource, args.user)
load_test_list(args.testlist)

if __name__ == '__main__':
    run_test()
