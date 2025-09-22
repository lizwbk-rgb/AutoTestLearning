#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据管理模块
--------------------------------------------------
- DataBase：负责读取 *元素层* 数据（YAML 格式），支持占位符替换
- DataDriver：负责读取 *用例层* 数据，支持 YAML / Excel 两种驱动方式
--------------------------------------------------
"""

import os
from string import Template
import yaml

# 项目内部公共库
from base_container import GlobalManager
from base_logger import Logger
from base_path import BasePath as BP
from utils import read_config_ini
from base_yaml import read_yaml
from base_excel import ExcelRead


logger = Logger('base_data.py').get_logger()


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def init_file_path(file_path):
    """
    递归遍历指定目录，返回 *文件名 → 绝对路径* 的映射字典

    参数
    ----
    file_path : str
        待扫描的根目录

    返回
    ----
    dict
        key   : 不带扩展名的文件名
        value : 文件绝对路径
    """
    doc_path = {}
    path = None
    # os.walk 返回三元组 (dirpath, dirnames, filenames)
    path_lists = [item for item in os.walk(file_path)]

    for lists_item in path_lists:
        for item in lists_item:
            if isinstance(item, str):
                # 记录当前目录
                path = item
            if isinstance(item, list):
                # 遍历当前目录下的文件
                for file_name in item:
                    # 去掉扩展名作为 key
                    key = file_name.split('.')[0]
                    doc_path[key] = os.path.join(path, file_name)
    return doc_path


def is_file_exist(file_path_map, file_name):
    """
    校验文件是否存在，不存在则抛异常

    参数
    ----
    file_path_map : dict
        init_file_path 生成的映射表
    file_name : str
        待查找的文件名（不含扩展名）

    返回
    ----
    str
        文件绝对路径
    """
    abs_path = file_path_map.get(file_name)
    if abs_path is None:
        raise FileNotFoundError(
            '{} 不存在，请检查文件名或配置文件中的 TEST_PROJECT！'.format(file_name)
        )
    return abs_path


# ---------------------------------------------------------------------------
# 元素层数据读取
# ---------------------------------------------------------------------------
class DataBase(object):
    """
    读取指定项目的元素层 YAML 数据，支持运行时动态替换占位符
    """

    def __init__(self, doc_name=None):
        # 全局单例，可用于跨模块共享数据
        self.gm = GlobalManager()

        # 元素文件名（不含扩展名）
        self.doc_name = doc_name

        # 读取全局配置文件 config.ini
        self.config = read_config_ini(BP.CONFIG_FILE)
        self.run_config = self.config['项目运行设置']

        # 根据 TEST_PROJECT 拼接出元素层根目录，并建立索引
        self.api_path = init_file_path(
            os.path.join(BP.DATA_ELEMENTS_DIR, self.run_config['TEST_PROJECT'])
        )
        print('[DataBase] 元素层索引表：', self.api_path)

        # 非客户端模式时，必须确保文件存在
        if self.run_config['AUTO_TYPE'] != 'CLIENT':
            self.abs_path = is_file_exist(self.api_path, self.doc_name)

    def get_data(self, change_data=None):
        """
        读取 YAML 并返回 Python 对象；支持占位符替换

        参数
        ----
        change_data : dict, optional
            用于替换 YAML 中 $placeholder 的字典，默认为 None

        返回
        ----
        dict / list
            反序列化后的 YAML 内容
        """
        if change_data:
            # 需要动态替换
            with open(self.abs_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                # 使用 string.Template 做安全替换
                changed_content = Template(raw_content).safe_substitute(**change_data)
                return yaml.safe_load(changed_content)
        else:
            # 直接读取
            return read_yaml(self.abs_path)


# ---------------------------------------------------------------------------
# 用例层数据读取
# ---------------------------------------------------------------------------
class DataDriver(object):
    """
    根据 DATA_DRIVER_TYPE 决定用例层数据源：
    - yaml_driver : 读取 YAML
    - excel_driver: 读取 Excel，返回 list[dict]
    """

    def __init__(self, doc_name=None):
        self.gm = GlobalManager()
        self.config = read_config_ini(BP.CONFIG_FILE)

    def get_case_data(self, doc_name=None):
        """
        读取指定用例文件

        参数
        ----
        doc_name : str, optional
            用例文件名（不含扩展名），默认为 None

        返回
        ----
        dict / list / None
            YAML 驱动：返回 dict / list
            Excel 驱动：返回 list[dict]，每行转换为一个字典
        """
        data_type = self.config['项目运行设置']['DATA_DRIVER_TYPE']
        test_project = self.config['项目运行设置']['TEST_PROJECT']

        # 拼接用例层根目录：data_driver / yaml_driver|excel_driver / project
        abs_path = init_file_path(
            os.path.join(BP.DATA_DRIVE_DIR, data_type, test_project)
        )
        data_path = is_file_exist(abs_path, doc_name)

        if data_type == 'yaml_driver':
            return read_yaml(data_path)
        elif data_type == 'excel_driver':
            return ExcelRead(data_path).dict_data()
        return None


# ---------------------------------------------------------------------------
# 本地调试入口
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    driver = DataDriver()
    result = driver.get_case_data('test')
    print(result)