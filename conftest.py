import base64
import pytest
from io import BytesIO
from py.xml import html
from base.utils import *
from base.base_path import BasePath as BP
from base.base_container import GlobalManager
from base.base_yaml import write_yaml

config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
insert_js_html = False


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store_true", default=config['WEB自动化配置']['browser'],
        help="browser option: firefox or chrome or ie"
    )
    parser.addoption(
        "--host", action="store", default=config['项目运行设置']['test_url'], help="test host->http://10.11.1.171:8888"
    )


@pytest.fixture(scope="function")
def driver(request):
    try:
        from selenium import webdriver
        test_driver = None
        driver_name = request.config.getoption("--browser")
        if driver_name == 'ie':
            test_driver = webdriver.Ie(executable_path=os.path.join(BP.DRIVER_DIR, 'IEDriverServer.exe'))
        elif driver_name == 'firefox':
            test_driver = webdriver.Firefox(executable_path=os.path.join(BP.DRIVER_DIR, 'gecokdriver.exe'))
        elif driver_name == 'chrome':
            test_driver = webdriver.Chrome(executable_path=os.path.join(BP.DRIVER_DIR, 'chromedriver.exe'))
        elif driver_name == 'chromeheadles':
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            test_driver = webdriver.Chrome(executable_path=os.path.join(BP.DRIVER_DIR, 'chromedriver.exe'))
            test_driver.set_window_size(1920, 1080)
        GlobalManager().set_value('driver', test_driver)
        test_driver.implicitly_wait(5)
        print("正在启动浏览器{}".format(driver_name))

        def quit_driver():
            print("当全部用例执行完成之后：teardown quit driver!")
            test_driver.quit()

        request.addfinalizer(quit_driver)
        return test_driver
    except ImportError:
        pytest.exit("未安装selenium")
    except Exception as e:
        pytest.exit("启动webdriver错误：{}".format(e))


def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([html.p("测试开发组：工具人1号")])


def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))
    cells.pop()


def pytest_html_results_table_row(report, cells):
    if hasattr(report, 'description'):
        cells.insert(1, html.td(report.description))
        cells.pop()
    else:
        print("！！！！！！", report.longreprtext)


def _capture_screenshot_sel():
    driver = GlobalManager().get_value('driver')
    if not driver:
        pytest.exit('driver获取为空')
    driver.get_screenshot_as_file(os.path.join(BP.SCREENSHOT_PIC))
    return driver.get_screenshot_as_base64()


def _capture_screenshot_pil():
    try:
        from PIL import ImageGrab
        output_buffer = BytesIO()
        img = ImageGrab.grab()
        img.save(BP.SCREENSHOT_PIC)
        img.save(output_buffer, 'PNG')
        bytes_value = output_buffer.getvalue()
        output_buffer.close()
        return base64.b64encode(bytes_value).decode('utf-8')
    except ImportError:
        pytest.exit('未安装PIL')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    pytest_html = item.config.pluginmanager.getplugin('html')
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):  # 失败截图
            if config['项目运行设置']['AUTO_TYPE'] == 'WEB':
                screen_img = _capture_screenshot_sel()
            elif config['项目运行设置']['AUTO_TYPE'] == 'CLIENT':
                screen_img = _capture_screenshot_pil()
            else:
                screen_img = None
            file_name = report.nodeid.replace("::", "_") + ".png"
            if config['项目运行设置']['REPORT_TYPE'] == 'HTML' and screen_img:
                if file_name:
                    html = '<div><img src="Data:image/png;base64,%s" alt="screenshot" style="width:600px;height:300px;" ' \
                           'onclick="lookimg(this.src)" align="right"/></div>' % screen_img
                    script = '''
                        <script>
                            function lookimg(str)
                            {
                                var newwin=window.open();
                                newwin.document.write("<img src="+str+" />");
                            }
                        </script>
                        '''
                    extra.append(pytest_html.extras.html(html))
                    if not insert_js_html:
                        extra.append(pytest_html.extras.html(script))
            elif config['项目运行设置']['REPORT_TYPE'] == 'ALLURE':
                import allure
                with allure.step('添加测试失败截图...'):
                    allure.attach.file(BP.SCREENSHOT_PIC, "测试失败截图", allure.attachment_type.PNG)
    report.extra = extra
    report.description = str(item.function.__doc__)

def pytest_collection_modifyitems(session, config, items):
    if '--co' in config.invocation_params.args:
        test_cases = {}
        for item in items:
            case_class_name = '::'.join(item.nodeid.split('::')[0:2])
            case_name = item.nodeid.split('::')[-1]
            if not test_cases.get(case_class_name, None):
                test_cases[case_class_name] = {}
            if not test_cases[case_class_name].get(case_name, None):
                test_cases[case_class_name]['comment'] = item.cls.__doc__
            test_cases[case_class_name][case_name] = item.function.__doc__
        temp_cases_path = BP.TEMP_CASES
        write_yaml(temp_cases_path, test_cases)

