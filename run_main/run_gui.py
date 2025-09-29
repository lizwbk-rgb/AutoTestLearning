import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  #根目录
sys.path.append(PROJECT_ROOT)
from base.base_container import GlobalManager
from base.base_send_email import HandleEmail
import pytest
import multiprocessing
import ctypes
from base.run_qt import run
from base.base_path import BasePath as BP
from base.utils import read_config_ini, delete_all_file
from contextlib import contextmanager
from base.base_yaml import read_yaml

config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
run_config = gm.get_value('CONFIG_INFO')['项目运行设置']


@contextmanager
def output_to_null():
    f = open(os.devnull, 'w')
    saved_stdout = sys.stdout
    sys.stdout = f
    yield
    sys.stdout = saved_stdout


def run_collect_testcase(_v):
    with output_to_null():
        try:
            test_pj = os.path.join(BP.TEST_SUITS_DIR, run_config['TEST_PROJECT'])
            res = pytest.main(['-s', '-q', '--co', test_pj])
        except Exception as e:
            sys.exit('收集用例时发生错误,{}'.format(e))
    if res == 0:
        _v.value = True
        print("收集用例成功，生成用例集testcases.yaml")


def run_main():
    try:
        datas = read_yaml(BP.TEST_CASES)
        testcases = []
        if not datas:
            print("未选择任何用例")
            return
        for module in datas.keys():
            for key in datas[module]:
                if key == "comment":
                    continue
                testcase = key
                testcase = os.path.join(BP.PROJECT_ROOT, module) + "::" + testcase
                testcases.append(testcase)
        if run_config['REPORT_TYPE'] == 'ALLURE':
            pytest.main(['-v', '--alluredir={}'.format(BP.ALLURE_RESULT_DIR), *testcases])
            os.system('allure generate {} -o {} --clean'.format(BP.ALLURE_RESULT_DIR, BP.ALLURE_REPORT_DIR))
            delete_all_file(BP.ALLURE_RESULT_DIR)
        elif run_config['REPORT_TYPE'] == 'HTML':
            report_path = os.path.join(BP.HTML_DIR, 'auto_reports.html')
            pytest.main(['-v', '--html={}'.format(report_path), '--self-contained-html', *testcases])
        elif run_config['REPORT_TYPE'] == 'XML':
            report_path = os.path.join(BP.XML_DIR, 'auto_reports.xml')
            pytest.main(['-v', '--junitxml={}'.format(report_path), *testcases])
        else:
            print("暂不支持此报告类型:{}".format(run_config['REPORT_TYPE']))
        # 邮件发送
        if run_config['IS_EMAIL'] == 'yes':
            el = HandleEmail()
            text = '本邮件由系统自动发出，无需回复！\n各位同事，大家好，以下为本次测试报告!'
            el.send_public_email(_text=text, file_type=run_config['REPORT_TYPE'])
            print("邮件发送成功：{}".format(run_config['REPORT_TYPE']))
    except FileNotFoundError:
        print("无用例文件,执行test_suits下所有用例")
        test_case = os.path.join(BP.TEST_SUITS_DIR, run_config['TEST_PROJECT'])
        pytest.main(['--html=auto_reports.html', '--self-contained-html', test_case])


def run_app(name, *args):
    app = multiprocessing.Process(target=name, args=args)
    app.start()
    app.join()


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    v = manager.Value(ctypes.c_bool, False)
    print("正在加载用例集，请稍后...")
    run_app(run_collect_testcase, v)
    if not v.value:
        sys.exit()
    run_app(run)
    run_main()
