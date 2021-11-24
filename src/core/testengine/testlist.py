# -*- coding:utf-8 -*-
# @Time: 2021/11/21 0021 22:13
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: testlist.py

import json
import os

from core.case.base import TestType
from core.config.setting import SettingBase, dynamic_setting


class TestListError(Exception):
    """
    用来描述测试列表的一系列错误异常
    """

    def __init__(self, message, ex=None):
        super().__init__("测试列表异常:" + message)
        self.parent = ex


@dynamic_setting
class TestList:
    """
    测试列表类
    """

    def __init__(self, filepath):
        self.filepath = filepath  # 存储测试列表的文件路径
        self.setting_file_path = None
        self.test_list_name = ""
        self.description = ""
        self.test_cases = []  # 存放该测试列表所包含的测试用例的名称和配置路径
        self.sub_list = []  # 用来存储子列表的实例

        # 读取[测试列表文件]路径, 并更新[测试设置文件]路径
        self.load()
        self.setting_path = os.path.dirname(self.setting_file_path)
        self.setting_file = os.path.basename(self.setting_file_path)

    def load(self):
        """
        读取测试列表
        """
        if not os.path.exists(self.filepath):
            raise TestListError("%s [测试列表]无法找到" % self.filepath)
        try:
            testlist_file = open(self.filepath)
            testlist_obj = json.load(testlist_file)
            self.test_list_name = testlist_obj['name']
            self.description = testlist_obj['description']
            self.setting_file_path = testlist_obj['setting_path']
            # 如果没有设置文件路径, 则采用默认路径
            if not self.setting_file_path:
                self.setting_file_path = os.path.join(os.path.dirname(self.filepath),
                                                      os.path.basename(self.filepath) + ".settings")
            # 遍历测试用例加入测试列表
            for testcase in testlist_obj['cases']:
                self.test_cases.append(testcase)

            # 加入子列表
            for sublist in testlist_obj['sublist']:
                full_path = os.path.join(os.path.dirname(self.filepath), sublist)
                temp_list = TestList(full_path)
                try:
                    temp_list.load()
                    self.sub_list.append(temp_list)
                except:
                    pass

        except Exception as ex:
            raise TestListError("打开文件%s错误" % self.filepath, ex)

    def save(self):
        """
        将测试列表保存成json格式的文件
        """
        json_obj = dict()
        json_obj['name'] = self.test_list_name
        json_obj['description'] = self.description
        json_obj['setting_path'] = self.setting_file_path
        json_obj['cases'] = list()
        for testcase in self.test_cases:
            json_obj['cases'].append(testcase)
        json_obj['sublist'] = list()
        for sublist in self.sub_list:
            try:
                sublist.save()
                json_obj['sublist'].append(os.path.basename(sublist.filepath))
            except:
                pass
        try:
            testlist_file = open(self.filepath, mode="w")
            json.dump(json_obj, testlist_file, indent=4)
        except Exception as ex:
            raise TestListError("无法保存测试列表%s" % self.filepath, ex)

    class TestListSetting(SettingBase):
        """
        测试列表的配置类
        让执行者根据 不同的测试需求 设置 测试列表的测试选项
        """
        random_seed = 0  # 随机树种子, 0表示每次产生新的随机数种子
        case_setting_path = ""
        skip_if_high_priority_failed = True
        follow_priority = True  # 测试用例不按照优先级来执行
        run_type = TestType.ALL  # 测试类型标识符, 该字段与[测试用例类型]字段进行"与"操作, 若为0, 则跳过测试用例的执行
        priority_to_run = []  # 指定运行哪些优先级的测试用例


if __name__ == "__main__":
    tl = TestList("demo_list.testlist")
    # tl2 = TestList("demo_list2.testlist")
    # tl2.test_list_name = "Demo sub list"
    # tl2.description = "desc"
    # tl.test_list_name = "A Demo Test List"
    # tl.description = "Description"
    # tl.setting_file_path = "."
    # tl.sub_list.append(tl2)
    # tl.test_cases.append("case1")
    # tl.test_cases.append("case2")
    # tl.save()
    tl.load()
    print(tl)
