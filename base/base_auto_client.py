#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端 UI 自动化通用库（基于 pyautogui）

本脚本提供两大核心能力：
1. Locator：图像识别定位（支持灰度/置信度/超时等配置）
2. Operator：鼠标、键盘、滚轮、文本输入等常用操作

所有配置均读取自 config.ini 的「客户端自动化配置」小节；
运行日志统一输出到 logs 目录，截图异常保存在 screenshots 目录。
"""

import os
import time
import pyautogui
import pyperclip
from base_data import DataBase          # 基础数据层（读取路径、配置等）
from utils import *                     # 工具函数
from base_logger import Logger          # 统一日志
from base_path import BasePath as BP    # 项目路径常量

# ---------------------------- 日志初始化 ----------------------------
logger = Logger('base_auto_client.py').get_logger()


# ===================================================================
#  Locator 类：负责“找图”
# ===================================================================
class Locator(DataBase):
    """
    通过图像识别在屏幕上定位元素。
    所有查找方法均返回 pyautogui.Point（中心坐标）或 None。
    """

    def __init__(self):
        super().__init__()
        # 读取 config.ini 中的「客户端自动化配置」
        cfg = self.config['客户端自动化配置']
        self.duration = float(cfg['duration'])        # 鼠标移动/拖拽的动画时长
        self.interval = float(cfg['interval'])        # 两次点击之间的间隔
        self.min_search_time = float(cfg['minSearchTime'])  # 图像识别最大等待时间
        self.confidence = float(cfg['confidence'])    # 图像识别置信度阈值
        self.gray_scale = bool(cfg['grayScale'])      # 是否启用灰度匹配

    # -------------------- 路径合法性检查 --------------------
    def is_path_exist(self, element: str) -> str:
        """
        根据元素名称（如 'qq.png'）返回绝对路径。
        若配置或文件缺失则抛 FileNotFoundError。
        """
        abs_path = self.api_path.get(element)
        if not abs_path:
            raise FileNotFoundError(
                f"{element} 不存在，请检查文件或 config.ini 内的相关配置")
        return abs_path

    # -------------------- 单图识别 --------------------
    def is_object_exist(self, element: str, search_time: float = None):
        """
        在屏幕上查找指定图片，返回中心坐标 Point；找不到返回 None。
        :param element: 图片文件名（带后缀）
        :param search_time: 最长搜索时间，默认读取 config
        """
        pic_path = self.is_path_exist(element)
        if search_time is None:
            search_time = self.min_search_time

        coordinates = pyautogui.locateOnScreen(
            pic_path,
            minSearchTime=search_time,
            confidence=self.confidence,
            grayscale=self.gray_scale
        )

        if coordinates:
            center = pyautogui.center(coordinates)
            logger.debug('查找对象 %s 存在，中心 %s', element.split('.')[0], center)
            return center

        logger.debug('查找对象 %s 不存在', element.split('.')[0])
        return None


# ===================================================================
#  异常辅助函数：截图 + 日志 + 抛异常
# ===================================================================
def _error_record(name: str, _type: str):
    """
    当图像识别失败时自动截图并记录日志，随后抛 ImageNotFoundException。
    """
    screenshot_path = os.path.join(BP.SCREENSHOT_DIR, f'{name}.png')
    pyautogui.screenshot(screenshot_path)
    logger.error('类型：%s，查找图片 %s 失败，已截图 %s', _type, name, screenshot_path)
    raise pyautogui.ImageNotFoundException


# ===================================================================
#  Operator 类：负责“操作”
# ===================================================================
class Operator(Locator):
    """
    在 Locator 的基础上封装鼠标、键盘、文本输入等常用操作。
    所有方法均支持日志记录与异常截图。
    """

    # -------------------- 单击/双击图标 --------------------
    def icon_click(self, element: str, position, clicks: int = 1,
                   is_click: bool = True, button: str = 'left'):
        """
        移动到图标中心并点击。
        :param element: 图片文件名（仅用于日志与异常）
        :param position: 已识别的坐标 (x, y)
        :param clicks: 点击次数
        :param is_click: False 则只移动不点击
        :param button: 'left'|'right'|'middle'
        """
        if not position:
            _error_record(element, 'click')

        pyautogui.moveTo(*position)
        if is_click:
            pyautogui.click(*position,
                            clicks=clicks,
                            button=button,
                            duration=self.duration,
                            interval=self.interval)
        logger.debug('鼠标移动到 %s 并点击 %s 次（%s）', element, clicks, button)

    # -------------------- 相对偏移点击 --------------------
    def rel_icon_click(self, positioned_element: str,
                       rel_x: int = 0, rel_y: int = 0,
                       clicks: int = 1, is_click: bool = True,
                       button: str = 'left'):
        """
        先识别基准图，再相对偏移 (rel_x, rel_y) 点击。
        """
        element_position = self.is_object_exist(positioned_element)
        if not element_position:
            _error_record(positioned_element, 'rel_pos_click')

        # 先移动到元素中心，再相对偏移
        pyautogui.moveTo(*element_position, duration=self.duration)
        pyautogui.moveRel(rel_x, rel_y, duration=self.duration)
        if is_click:
            pyautogui.click(clicks=clicks,
                            button=button,
                            duration=self.duration,
                            interval=self.interval)
        logger.debug('定位元素 %s，原位置 %s，偏移 %s，点击 %s 次',
                     positioned_element, element_position, (rel_x, rel_y), clicks)

    # -------------------- 绝对坐标点击 --------------------
    def position_click(self, pos_x: int = None, pos_y: int = None,
                       clicks: int = 1, button: str = 'left'):
        pyautogui.click(pos_x, pos_y,
                        clicks=clicks,
                        button=button,
                        duration=self.duration,
                        interval=self.interval)
        logger.debug('鼠标在绝对坐标 (%s, %s) 点击 %s 键 %s 次', pos_x, pos_y, button, clicks)

    # -------------------- 相对当前位置点击 --------------------
    def rel_position_click(self, rel_x: int = None, rel_y: int = None,
                           clicks: int = 1, button: str = 'left'):
        pyautogui.move(rel_x, rel_y, duration=self.duration)
        pyautogui.click(clicks=clicks,
                        button=button,
                        duration=self.duration,
                        interval=self.interval)
        logger.debug('鼠标相对当前位置 (%s, %s) 点击 %s 键 %s 次', rel_x, rel_y, button, clicks)

    # -------------------- 移动 --------------------
    def moveto(self, pos_x: int = None, pos_y: int = None, relative: bool = False):
        if relative:
            pyautogui.moveRel(pos_x, pos_y, duration=self.duration)
            logger.debug('鼠标相对移动 (%s, %s)', pos_x, pos_y)
        else:
            pyautogui.moveTo(pos_x, pos_y, duration=self.duration)
            logger.debug('鼠标移动到 (%s, %s)', pos_x, pos_y)

    # -------------------- 拖拽 --------------------
    def dragto(self, pos_x: int = None, pos_y: int = None,
               button: str = 'left', relative: bool = False):
        if relative:
            pyautogui.dragRel(pos_x, pos_y, button=button, duration=self.duration)
            logger.debug('鼠标相对拖拽 (%s, %s)', pos_x, pos_y)
        else:
            pyautogui.dragTo(pos_x, pos_y, button=button, duration=self.duration)
            logger.debug('鼠标拖拽到 (%s, %s)', pos_x, pos_y)

    # -------------------- 滚轮 --------------------
    @staticmethod
    def scroll(scroll_distance: int, move_to_x: int = None, move_to_y: int = None):
        pyautogui.scroll(scroll_distance, move_to_x, move_to_y)
        logger.debug('鼠标在 (%s, %s) 滚动 %s 格', move_to_x, move_to_y, scroll_distance)

    # -------------------- 中文输入（剪贴板方案） --------------------
    @staticmethod
    def chinese_input(text: str):
        """
        通过剪贴板实现中文输入，避免 pyautogui 无法直接输入中文的问题。
        支持多行文本（按 Enter 分割）。
        """
        if not text:
            return
        paragraphs = text.split('\n')
        for idx, paragraph in enumerate(paragraphs):
            if paragraph:
                pyperclip.copy(paragraph)
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.1)
            if idx < len(paragraphs) - 1:
                pyautogui.press('enter')
                time.sleep(0.05)

    # -------------------- 通用文本输入 --------------------
    def text_input(self, text: str):
        """
        自动判断中英文：
        - 含中文 -> 走剪贴板
        - 纯英文 -> 直接 pyautogui.write
        """
        has_chinese = any('\u4e00' <= ch <= '\u9fff' for ch in text)
        if has_chinese:
            self.chinese_input(text)
        else:
            pyautogui.write(text, interval=self.interval)

    # -------------------- 单键 --------------------
    @staticmethod
    def press(key: str):
        pyautogui.press(key)
        logger.debug('按下键盘按键 %s', key)

    # -------------------- 组合键 --------------------
    @staticmethod
    def hotkey(*keys):
        pyautogui.hotkey(*keys)
        logger.debug('执行组合键 %s', keys)


# ===================================================================
#  简单自测示例
# ===================================================================
if __name__ == '__main__':
    # 1. 检查配置与路径
    image = Locator()
    image.is_path_exist('qq.png')

    # 2. 在屏幕上找 QQ 图标，最多等 5 秒
    position = image.is_object_exist('qq.png', search_time=5)
    print('QQ 图标中心坐标：', position)

    # 3. 找到后双击
    if position:
        time.sleep(5)   # 给用户时间切到桌面
        op = Operator()
        op.icon_click(element='qq.png', position=position, clicks=2)