# -*- coding:utf-8 -*-
# @Time: 2021/11/19 0019 21:37
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: demo_module.py
from core.config.logic_module import ModuleBase, ModuleType
from core.config.setting import dynamic_setting, SettingBase
from core.resource.pool import ResourcePool
from core.result.reporter import ResultReporter, StepInfo


@dynamic_setting
class DemoModule(ModuleBase):
    """
    示例模块, 会在测试用例执行前输出一个INFO信息
    """
    module_type = ModuleType.POST
    priority = 0

    def __init__(self, report: ResultReporter, resource: ResourcePool, **kwargs):
        # 每个模块有自己的日志文件与报告
        super().__init__(report, resource)
        # 每个模块有自己的设置文件与路径
        self.setting_path = kwargs.get("setting_path", "")
        self.setting_file = kwargs.get("setting_file")

    def action(self):
        self.reporter.add(StepInfo.INFO, "这是一个demo模块")
        self.reporter.add(StepInfo, f"setting value:{self.setting.setting_value}")

    def stop(self):
        pass

    # 嵌套类, 通过setting中的setting_value从外部获取参数
    class ModuleSetting(SettingBase):
        setting_value = "一个值"
