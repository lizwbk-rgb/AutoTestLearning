# run_main/run.py
import os
import sys
import pytest
import subprocess

# ---------- 环境变量 ----------
# 把 JAVA_HOME 注入当前进程，避免 allure 再次报找不到 Java
os.environ['JAVA_HOME'] = r'D:\application\Java\jdk-11'
os.environ['PATH'] = os.environ.get('PATH', '') + r';D:\application\Java\jdk-11\bin'

# ---------- 项目根目录 ----------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# ---------- 引入业务模块 ----------
from base.base_path import BasePath as BP
from base.utils import read_config_ini, delete_all_file
from base.base_container import GlobalManager
from base.base_send_email import HandleEmail

# ---------- 读取全局配置 ----------
config = read_config_ini(BP.CONFIG_FILE)
gm = GlobalManager()
gm.set_value('CONFIG_INFO', config)
gm.set_value('DATA_DRIVER_PATH',
             os.path.join(BP.DATA_DRIVE_DIR, config['项目运行设置']['DATA_DRIVER_TYPE']))

# ---------- allure 路径 ----------
allure_path = r'C:\Users\v_zhquanli\PycharmProjects\AutoTestLearning\ext_tools\allure-2.35.1\bin\allure.bat'
result_dir = BP.ALLURE_RESULT_DIR
report_dir = BP.ALLURE_REPORT_DIR

print(f'Allure path: {allure_path}')
print(f'Result dir : {result_dir}')
print(f'Report dir : {report_dir}')

# ---------- 首次生成报告（脚本启动时） ----------
if not os.path.exists(result_dir):
    print(f'Result directory does not exist: {result_dir}')
    sys.exit(1)

subprocess.run([allure_path, 'generate', result_dir,
                '-o', report_dir, '--clean'], check=True)
print('Allure generate command executed successfully.')


# ---------- 主运行函数 ----------
def run_main():
    run_config = gm.get_value('CONFIG_INFO')['项目运行设置']
    test_case = os.path.join(BP.TEST_SUITS_DIR, run_config['TEST_PROJECT'])
    print(f'Test case directory: {test_case}')

    if run_config['REPORT_TYPE'] == 'ALLURE':
        # 运行 pytest 生成 json 结果
        pytest.main(['-v', f'--alluredir={BP.ALLURE_RESULT_DIR}', test_case])
        # 生成最终 html 报告
        subprocess.run([allure_path, 'generate', BP.ALLURE_RESULT_DIR,
                        '-o', BP.ALLURE_REPORT_DIR, '--clean'], check=True)
        delete_all_file(BP.ALLURE_REPORT_DIR)

    elif run_config['REPORT_TYPE'] == 'HTML':
        report_path = os.path.join(BP.HTML_DIR, 'auto_report.html')
        pytest.main(['-v', f'--html={report_path}', '--self-contained-html', test_case])

    elif run_config['REPORT_TYPE'] == 'XML':
        report_path = os.path.join(BP.XML_DIR, 'auto_report.xml')
        pytest.main(['-v', f'--junitxml={report_path}', test_case])

    else:
        print(f"暂不支持此报告类型：{run_config['REPORT_TYPE']}")
        return

    # ---------- 邮件 ----------
    if run_config.get('IS_EMAIL') == 'yes':
        elem = HandleEmail()
        text = '本邮件由系统自动发出，无需回复！\n各位同事，大家好！以下是本次测试报告。'
        elem.send_public_email(text, run_config['REPORT_TYPE'])
        print(f"邮件发送成功：{run_config['REPORT_TYPE']}")


# ---------- 入口 ----------
if __name__ == '__main__':
    run_main()
