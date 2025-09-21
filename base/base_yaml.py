# -*- coding: utf-8 -*-
"""
YAML 读写工具
依赖：PyYAML（pip install pyyaml）
"""

import yaml
import os


def read_yaml(path: str) -> dict:
    """
    读取 YAML 文件并返回 Python 对象（通常是 dict）
    :param path: 文件绝对/相对路径
    :return: 反序列化后的 Python 对象
    :raises FileNotFoundError: 当路径不存在时
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} 路径不存在')

    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}   # 空文件返回空 dict，避免 None


def write_yaml(path: str, data: dict) -> None:
    """
    将 Python 对象序列化后写入 YAML 文件
    :param path: 目标文件路径（若不存在则自动创建）
    :param data: 要写入的 Python 对象（推荐 dict/list）
    """
    # 确保所在目录存在
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)