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

def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store_true", default=config['WEB自动化配置']['browser'], help="browser option: firefox or chrome or ie"
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