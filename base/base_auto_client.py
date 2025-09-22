import time
import pyautogui
import pyperclip
from base_data import DataBase
from utils import *
from base_logger import Logger
from base_path import BasePath as BP

logger = Logger('base_auto_client.py').get_logger()


class Locator(DataBase):
    def __init__(self):
        super().__init__()
        self.duration = float(self.config['客户端自动化配置']['duration'])
        self.interval = float(self.config['客户端自动化配置']['interval'])
        self.min_search_time = float(self.config['客户端自动化配置']['minSearchTime'])
        self.confidence = float(self.config['客户端自动化配置']['confidence'])
        self.gray_scale = bool(self.config['客户端自动化配置']['grayScale'])

    def is_path_exist(self, element):
        abs_path = self.api_path.get(element)
        if not abs_path:
            raise FileNotFoundError(f"{element}不存在，请检查文件或config.ini文件内的相关配置")
        return abs_path

    def is_object_exist(self, element, search_time=None):
        pic_path = self.is_path_exist(element)
        if not search_time:
            search_time = self.min_search_time
        coordinates = pyautogui.locateOnScreen(pic_path, minSearchTime=search_time, confidence=self.confidence,
                                               grayscale=True)
        if coordinates:
            logger.debug('查找对象{}存在'.format(element.split('.')[0]))
            return pyautogui.center(coordinates)
        logger.debug('查找对象{}不存在'.format(element.split('.')[0]))
        return None


def _error_record(name, _type):
    pyautogui.screenshot(os.path.join(BP.SCREENSHOT_DIR, name + '.png'))
    logger.error(f'类型：{_type},查找图片{name}位置，当前屏幕无此内容，已截图。')
    raise pyautogui.ImageNotFoundException


class Operator(Locator):
    def click(self, element, position, clicks=1, is_click=True, button='left'):
        if not position:
            _error_record(element, 'click')
        pyautogui.moveTo(*position)
        if is_click:
            pyautogui.click(*position, clicks=clicks, button=button, duration=self.duration, interval=self.interval)
        logger.debug(f'鼠标移动到图片{element}的位置{is_click}，点击{position}成功')


if __name__ == '__main__':
    image = Locator()
    image.is_path_exist('qq')
    position = image.is_object_exist('qq', search_time=5)
    print(position)
    time.sleep(5)
    op = Operator()
    op.click(element='qq', position=position, clicks=2)
