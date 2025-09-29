# -*- coding: utf-8 -*-
"""
接口自动化底层封装
--------------------------------
- 统一 YAML 管理接口定义
- 统一 session 保持会话
- 统一日志、异常与超时处理
"""

import requests
import urllib3
from urllib.parse import urljoin          # 拼接相对/绝对 URL
from urllib3.exceptions import InsecureRequestWarning  # 关闭 HTTPS 警告用

from base.base_data import DataBase            # 读取 YAML/Excel 基础类
from base.base_logger import Logger            # 自研日志封装

# 生成当前文件的日志实例
logger = Logger('base_auto_api.py').get_logger()


# ==========================
# 接口底层核心类
# ==========================
class ApiBase(DataBase):
    """
    所有接口用例层的父类，负责：
    1. 解析 YAML 获得请求模板
    2. 自动拼接 host + path
    3. 统一发送请求、记录日志
    """

    # 整个进程共享同一个 session，自动携带 cookie/authorization
    session = requests.Session()

    def __init__(self, yaml_name: str):
        """
        :param yaml_name: YAML 文件名（无需 .yaml 后缀）
        """
        super().__init__(yaml_name)      # 加载 YAML 数据
        self.yaml_name = yaml_name       # 保留文件名，方便日志
        self.timeout = 5                 # 默认超时 5 秒（也可通过 kwargs 覆盖）

    # -------------------------------------------------
    # 统一请求入口：所有 HTTP 方法都走这里
    # -------------------------------------------------
    def request_base(self, api_name: str, change_data=None, **kwargs):
        """
        根据 YAML 中定义的接口模板发送请求
        :param api_name:     YAML 中接口节点名称，如 login_api
        :param change_data:  动态替换模板中的 {placeholder}
        :param kwargs:       可覆盖 YAML 中的任何字段（method/url/data/json/headers...）
        :return:             requests.Response 对象
        """
        try:
            # ① 日志：开始调用
            logger.info('【%s：%s 接口调用开始】', self.yaml_name, api_name)

            # ② 读取并合并 YAML 模板
            yaml_dict = self.get_data(change_data)[api_name]          # 解析后的字典
            yaml_dict['url'] = urljoin(self.run_config['TEST_URL'],  # 自动拼接 host + path
                                       yaml_dict['url'])

            # ③ 日志：打印完整请求数据
            logger.info('【获取 %s 文件 %s 接口请求数据：%s】', self.yaml_name, api_name, yaml_dict)
            logger.info('【接口请求方式：%s】', yaml_dict['method'])
            logger.info('【接口请求地址：%s】', yaml_dict['url'])
            if 'data' in yaml_dict:
                logger.info('【接口请求体(data)：%s】', yaml_dict['data'])
            elif 'json' in yaml_dict:
                logger.info('【接口请求体(json)：%s】', yaml_dict['json'])

            # ④ 关闭 SSL 警告（仅对当前请求生效）
            urllib3.disable_warnings(InsecureRequestWarning)

            # ⑤ 真正发请求（允许 kwargs 覆盖 YAML 任何字段）
            result = ApiBase.session.request(**yaml_dict, **kwargs)

            # ⑥ 日志：响应码 & 响应体（debug 级别）
            logger.debug('【接口响应码：%s】', result.status_code)
            logger.debug('【接口响应体：%s】', result.text)

            # ⑦ 日志：调用结束
            logger.info('【%s：%s 接口调用结束】', self.yaml_name, api_name)
            return result

        except Exception as e:
            logger.error('【接口请求失败！原因：%s】', e)
            raise


# ==========================
# 脚本自测入口
# ==========================
if __name__ == '__main__':
    # 示例：加载名为“接口元素信息-登录”的 YAML，并调用其中 home_api 接口
    api_base = ApiBase('接口元素信息-登录')
    resp = api_base.request_base('home_api')
    print(resp.text)