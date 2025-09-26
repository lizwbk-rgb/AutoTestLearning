import os
import sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from base.base_path import BasePath as BP
from base.utils import read_config_ini, delete_all_file
from base.base_container import GlobalManager
from base.base_send_email import HandleEmail

config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
gm.set_value('DATA_DRIVER_PATH', os.path.join(BP.DATA_DRIVE_DIR, config['项目运行设置']['DATA_DRIVER_TYPE']))


def run_main():
    run_config = gm.get_value('CONFIG_INFO')['项目运行设置']
    test_case = os.path.join(BP.TEST_SUITS_DIR, run_config['TEST_PROJECT'])
    if run_config['REPORT_TYPE'] == 'ALLURE':
        pytest.main(['-v', '--alluredir={}'.format(BP.ALLURE_RESULT_DIR), test_case])
        os.system('allure generate {} -o {} --clean'.format(BP.ALLURE_RESULT_DIR, BP.ALLURE_REPORT_DIR))
        delete_all_file(BP.ALLURE_REPORT_DIR)
    elif run_config['REPORT_TYPE'] == 'HTML':
        report_path = os.path.join(BP.HTML_DIR, 'auto_report.html')
        pytest.main(['-v', '--html={}'.format(report_path), '--self-contained-html', test_case])
    elif run_config['REPORT_TYPE'] == 'XML':
        report_path = os.path.join(BP.XML_DIR, 'auto_report.xml')
        pytest.main(['-v', '--junitxml={}'.format(report_path), test_case])
    else:
        print("暂不支持此报告类型：{}".format(run_config['REPORT_TYPE']))
    if run_config['IS_MAIL'] == 'yes':
        element = HandleEmail()
        text = '本邮件由系统自动发出，无需回复！\n各位同事，大家好！以下是本次测试报告。'
        element.send_public_email(text, run_config['REPORT_TYPE'])
        print("邮件发送成功：{}".format(run_config['REPORT_TYPE']))


if __name__ == '__main__':
    run_main()
