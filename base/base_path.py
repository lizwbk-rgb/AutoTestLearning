import os


class BasePath(object):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
    CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.ini')
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    DATA_DRIVE_DIR = os.path.join(DATA_DIR, 'data_driver')
    DATA_ELEMENTS_DIR = os.path.join(DATA_DIR, 'data_elements')
    DATA_TEMP_DIR = os.path.join(DATA_DIR, 'temp')
    SCREENSHOT_DIR = os.path.join(DATA_TEMP_DIR, 'screenshots')
    DRIVER_DIR = os.path.join(DATA_DIR, 'driver')
    LOG_DIR = os.path.join(PROJECT_ROOT, 'log')
    ALLURE_DIR = os.path.join(PROJECT_ROOT, 'reports', 'allure')
    ALLURE_REPORT_DIR = os.path.join(ALLURE_DIR, 'report')
    ALLURE_RESULT_DIR = os.path.join(ALLURE_DIR, 'result')
    HTML_DIR = os.path.join(PROJECT_ROOT, 'reports', 'html')
    XML_DIR = os.path.join(PROJECT_ROOT, 'reports', 'xml')
