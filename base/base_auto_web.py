# -*- coding: utf-8 -*-
"""
web 端 UI 自动化底层公共库
--------------------------------------------
- 基于 Selenium 二次封装
- 支持 yaml 管理元素定位表达式
- 提供常用页面操作（点击、输入、切换 iframe、窗口、弹窗、下拉框、鼠标键盘等）
"""

# ---------- Selenium 官方模块 ----------
from selenium.webdriver.remote.webelement import WebElement  # 元素对象类型标注
from selenium.webdriver.support.wait import WebDriverWait    # 显式等待
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select         # 下拉框处理
from selenium.webdriver.common.action_chains import ActionChains  # 鼠标/键盘链式操作
from selenium.common.exceptions import TimeoutException      # 超时异常

# ---------- 业务基础模块 ----------
from base.base_data import DataBase   # 读取 yaml/Excel 等测试数据基类
from base.base_logger import Logger        # 自研日志封装

# ---------- 日志对象 ----------
logger = Logger('base_auto_web.py').get_logger()


# ==========================
#  元素定位器 —— 负责“找到元素”
# ==========================
class Locator(DataBase):
    """
    解析 yaml 中的元素定位表达式，并返回 Selenium 元素对象
    """

    def __init__(self, yaml_name: str):
        """
        :param yaml_name: yaml 文件名称（无需 .yaml 后缀）
        """
        super().__init__(yaml_name)          # 加载 yaml 数据
        self.driver = self.gm.get_value('driver')  # 从全局管理器获取浏览器驱动实例
        self.time = 0.5                        # 轮询间隔
        self.timeout = 5                       # 默认最大等待时间

    # ----------------------
    #  解析 yaml 中的定位表达式
    # ----------------------
    def get_locator_data(self, items: str, change_data=None):
        """
        将 "页面/元素" 字符串解析成 Selenium 需要的 (by, value) 元组
        :param items:       例 "login/loginbtn"
        :param change_data: 动态替换定位符中的 {placeholder}
        :return:            (By.ID, "kw") / (By.XPATH, "//div[text()='{}']") ...
        """
        _element = self.get_data(change_data)      # 支持数据驱动替换
        item = items.split('/')                    # 支持多级索引，如 page/element
        element_data = tuple(_element[item[0]][item[1]])  # 取出 (by, value)
        return element_data

    # ----------------------
    #  显式等待查找单个/全部元素
    # ----------------------
    def find_element(self, items: str, change_data=None, is_all=False) -> WebElement:
        """
        显式等待直到元素出现在 DOM 中
        :param items:
        :param change_data:
        :param is_all: False 返回单个 WebElement；True 返回 List[WebElement]
        """
        locator = self.get_locator_data(items, change_data)
        try:
            if not isinstance(locator, tuple):
                logger.error('element参数类型错误，必须传列表或元组类型，element = ["id","value"]')
            logger.debug('正在定位元素信息：定位方式=%s，value=%s', locator[0], locator[1])

            if not is_all:
                _element = WebDriverWait(self.driver, self.timeout, self.time).until(
                    EC.presence_of_element_located(locator))
            else:
                _element = WebDriverWait(self.driver, self.timeout, self.time).until(
                    EC.presence_of_all_elements_located(locator))

            logger.debug('定位元素 %s 成功', locator)
            return _element
        except TimeoutException as e:
            logger.error('未定位到元素 %s', locator)
            raise e


# ==========================
#  操作类 —— 负责“对元素做动作”
# ==========================
class Operator(Locator):
    """
    继承 Locator，提供各种高频页面行为封装
    """

    # ---------- 浏览器级别 ----------
    def get_url(self, url: str):
        """打开网址并最大化窗口"""
        self.driver.get(url)
        self.driver.maximize_window()
        logger.debug('浏览器访问地址：%s', url)

    # ---------- 元素级基本操作 ----------
    def click(self, locator: str, change_data=None):
        """单击"""
        try:
            _element = self.find_element(locator, change_data)
            _element.click()
            logger.debug('点击 %s 成功', locator)
        except Exception as e:
            logger.error('点击 %s 失败', locator)
            raise e

    def send_keys(self, locator: str, keys='', change_data=None):
        """输入文本"""
        try:
            _element = self.find_element(locator, change_data)
            _element.send_keys(keys)
            logger.debug('输入文本 %s 成功', keys)
        except Exception as e:
            logger.error('输入文本 %s 失败', keys)
            raise e

    def clear(self, locator: str, change_data=None):
        """清空输入框"""
        try:
            _element = self.find_element(locator, change_data)
            _element.clear()
            logger.debug('清空 %s 成功', locator)
        except Exception as e:
            logger.error('清空 %s 失败', locator)
            raise e

    # ---------- 获取信息 ----------
    def get_title(self):
        """获取页面 title"""
        try:
            title = self.driver.title
            logger.debug('获取 title 成功：%s', title)
            return title
        except:
            logger.error('获取 title 失败')
            return ''

    def get_text(self, locator: str, change_data=None):
        """获取元素文本"""
        try:
            content = self.find_element(locator, change_data).text
            logger.debug('获取文本成功：%s', content)
            return content
        except:
            logger.error('获取文本失败')
            return ''

    def get_attribute(self, locator: str, name: str, change_data=None):
        """获取元素属性值"""
        try:
            _element = self.find_element(locator, change_data)
            attr = _element.get_attribute(name)
            logger.debug('获取属性 %s 成功：%s', name, attr)
            return attr
        except:
            logger.error('获取属性 %s 失败', name)
            return ''

    # ---------- 布尔断言 ----------
    def is_selected(self, locator: str, change_data=None):
        """复选/单选框是否被选中"""
        _element = self.find_element(locator, change_data)
        return _element.is_selected()

    def is_title(self, _title=''):
        """显式等待页面 title 完全等于预期"""
        try:
            return WebDriverWait(self.driver, self.timeout, self.time).until(EC.title_is(_title))
        except:
            return False

    def is_title_contains(self, _title=''):
        """显式等待页面 title 包含预期字符串"""
        try:
            return WebDriverWait(self.driver, self.timeout, self.time).until(EC.title_contains(_title))
        except:
            return False

    def is_text_in_element(self, locator: str, _text='', change_data=None):
        """显式等待指定元素文本包含预期字符串"""
        try:
            locator = self.get_locator_data(locator, change_data)
            return WebDriverWait(self.driver, self.timeout, self.time).until(
                EC.text_to_be_present_in_element(locator, _text))
        except:
            return False

    def is_value_in_element(self, locator: str, _value='', change_data=None):
        """显式等待指定元素 value 属性包含预期字符串"""
        try:
            locator = self.get_locator_data(locator, change_data)
            return WebDriverWait(self.driver, self.timeout, self.time).until(
                EC.text_to_be_present_in_element_value(locator, _value))
        except:
            return False

    def is_alert(self):
        """判断弹窗是否出现，若出现则返回 alert 对象"""
        try:
            return WebDriverWait(self.driver, self.timeout, self.time).until(EC.alert_is_present())
        except:
            return False

    # ---------- 鼠标 ----------
    def mouse_moveto(self, locator: str, change_data=None):
        """鼠标悬停+单击"""
        _element = self.find_element(locator, change_data)
        ActionChains(self.driver).move_to_element(_element).click().perform()
        logger.info('鼠标悬停并单击 %s', locator)

    def mouse_dragto(self, locator: str, x_offset: int, y_offset: int, change_data=None):
        """拖拽元素到相对坐标"""
        _element = self.find_element(locator, change_data)
        ActionChains(self.driver).drag_and_drop_by_offset(_element, x_offset, y_offset).perform()
        logger.info('拖拽 %s 偏移 (%s, %s)', locator, x_offset, y_offset)

    # ---------- 滚动 ----------
    def scroll_to_element(self, locator: str, change_data=None):
        """滚动到元素可见"""
        target = self.find_element(locator, change_data)
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        logger.info('滚动至元素 %s', locator)

    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo(0,0)")
        logger.info('滚动到顶部')

    def scroll_to_end(self, x=0):
        """滚动到页面底部"""
        self.driver.execute_script(f"window.scrollTo({x},document.body.scrollHeight)")
        logger.info('滚动到底部')

    # ---------- 键盘 ----------
    def keyboard_send_keys(self, locator: str, keys, change_data=None):
        """在指定元素上键盘输入"""
        _element = self.find_element(locator, change_data)
        ActionChains(self.driver).send_keys(_element, keys).perform()
        logger.info('键盘在 %s 输入 %s', locator, keys)

    # ---------- 弹窗 ----------
    def get_alert_content(self):
        """获取 alert 文本"""
        confirm = self.driver.switch_to.alert
        logger.info('获取弹窗文本：%s', confirm.text)
        return confirm.text

    def accept_alert(self):
        """alert 点确定"""
        confirm = self.driver.switch_to.alert
        confirm.accept()
        logger.info('弹窗点击接受')

    def dismiss_alert(self):
        """alert 点取消"""
        confirm = self.driver.switch_to.alert
        confirm.dismiss()
        logger.info('弹窗点击取消')

    def input_alert(self, text: str):
        """prompt 弹窗输入文本"""
        prompt = self.driver.switch_to.alert
        prompt.send_keys(text)
        logger.info('弹窗输入文本：%s', text)

    # ---------- 下拉框 ----------
    def select_list_by_index(self, locator: str, index=0, change_data=None):
        """下拉框按索引选择"""
        _element = self.find_element(locator, change_data)
        Select(_element).select_by_index(index)
        logger.info('下拉框 %s 按索引选择 %s', locator, index)

    def select_list_by_value(self, locator: str, value, change_data=None):
        """下拉框按 value 选择"""
        _element = self.find_element(locator, change_data)
        Select(_element).select_by_value(value)
        logger.info('下拉框 %s 按 value 选择 %s', locator, value)

    def select_list_by_text(self, locator: str, text, change_data=None):
        """下拉框按可见文本选择"""
        _element = self.find_element(locator, change_data)
        Select(_element).select_by_visible_text(text)
        logger.info('下拉框 %s 按文本选择 %s', locator, text)

    # ---------- iframe 切换 ----------
    def switch_in_iframe(self, locator, change_data=None):
        """
        支持三种形式切换 iframe：
        1. id 或 name 字符串
        2. 索引 int
        3. WebElement 对象（元组定位）
        """
        try:
            id_index_locator = self.get_locator_data(locator, change_data)
            if isinstance(id_index_locator, (str, int)):
                self.driver.switch_to.frame(id_index_locator)
            elif isinstance(id_index_locator, (list, tuple)):
                _element = self.find_element(locator)
                self.driver.switch_to.frame(_element)
            logger.info('已切换 iframe：%s', id_index_locator)
        except Exception as e:
            logger.error('iframe 切换异常：%s', e)

    def switch_out_iframe_outermost(self):
        """切回最外层页面"""
        try:
            self.driver.switch_to.default_content()
            logger.info('iframe 切换到最外层')
        except Exception as e:
            logger.error('iframe 切换到最外层失败：%s', e)

    def switch_out_iframe_parent(self):
        """切回上一层 iframe"""
        try:
            self.driver.switch_to.parent_frame()
            logger.info('iframe 切换到上一层')
        except Exception as e:
            logger.error('iframe 切换到上一层失败：%s', e)

    # ---------- 窗口句柄 ----------
    def get_handle(self):
        """获取所有窗口句柄"""
        try:
            handles = self.driver.window_handles
            logger.info('获取所有句柄：%s', handles)
            return handles
        except Exception as e:
            logger.error('获取句柄失败：%s', e)

    def switch_handle(self, index=-1):
        """
        切换窗口/标签页
        :param index: -1 表示最新打开的窗口
        """
        try:
            handle_list = self.driver.window_handles
            self.driver.switch_to.window(handle_list[index])
            logger.info('切换句柄成功：%s', index)
        except Exception as e:
            logger.error('切换句柄失败：%s', e)


# ==========================
#  脚本自测入口
# ==========================
if __name__ == '__main__':
    element = Locator('Web元素信息-登录')
    res = element.get_locator_data('login/loginbtn')
    print(res)