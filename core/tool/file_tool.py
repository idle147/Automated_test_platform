# -*- coding:utf-8 -*-
# @Time: 2021/11/20 0020 16:49
# @Type: py file
# @Author: yangxin
# @Email: 2827709585@qq.com
# @File: file_tool.py
import os
import zipfile


class FileTool(object):
    """
    自定义的文件对象, 支持with语句
    """

    # def __init__(self, filename):
    #     self.filename = filename
    #     self.handler = None
    #
    # def __enter__(self):
    #     print("打开文件" + self.filename)
    #     self.handler = open(self.filename)
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     if self.handler is not None:
    #         self.handler.close()
    #     if exc_type is None:
    #         print("运行正常")
    #         return True
    #     else:
    #         print(exc_type)
    #         return False

    @staticmethod
    def zip_directory(dir_path, output_file):
        """
        将目标文件夹压缩成zip包并且输出到output_file
        并且将文件删除
        """
        zip = zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(dir_path, topdown=False):
            target_path = path.replace(dir_path, '')  # 去除前面的绝对路径
            for filename in filenames:
                # 跳过本身文件
                if os.path.join(path, filename) == output_file:
                    continue
                # 压缩目标文件, 删除源文件
                zip.write(os.path.join(path, filename), os.path.join(target_path, filename))
                os.remove(os.path.join(path, filename))
            # 删除源文件夹
            if target_path != '':
                os.rmdir(path)
        zip.close()

    @staticmethod
    def check_and_create_directory(filename):
        """
        检测目录是否存在， 不存在就创建
        @param filename:
        @return:
        """
        dir_name = os.path.dirname(filename)
        if dir_name == '':
            return
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
