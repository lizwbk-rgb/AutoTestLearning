import os.path
import time
from base.base_path import BasePath as BP
from ext_tools.system_helper import SystemOperation
from base.base_auto_client import Operator, Locator
from base.base_logger import Logger

logger = Logger('client_start_stop.py').get_logger()


class ClientStartStopPage(Operator, Locator):

    def __init__(self):
        super().__init__()
        self.project_path = BP.PROJECT_ROOT
        self.client_path = os.path.join(self.project_path, r'test_object\学生管理系统\客户端程序')
        self.exe_path = os.path.join(self.client_path, 'main.exe')
        self.db_path = os.path.join(self.client_path, 'student.db')
        self.sys = SystemOperation()

    def start_client(self):
        self.sys.popen_cmd('cd {} && start {}'.format(self.client_path, self.exe_path))
        logger.info('Start Client Start')

    def close_client(self):
        self.sys.popen_cmd('cd {} & taskkill /f /t /im {}'.format(self.client_path, "main.exe"))
        logger.info('Close Client Start')

    def load_client(self, username, password):
        self.rel_positioner_click('student_id', 150)
        self.text_input(username)
        logger.info('学号{}输入成功！'.format(username))
        self.rel_positioner_click('password', 150)
        self.text_input(password)
        logger.info('密码{}输入成功！'.format(password))
        self.positioner_click('stu_teacher_login')

    def assert_login(self, flog):
        if flog == 'student':
            assert self.is_object_exist('stu_login_success')
            logger.info('【断言】学生账号登录成功！')
        elif flog == 'teacher':
            assert self.is_object_exist('teacher_login_success')
            logger.info('【断言】教师账号登录成功！')


if __name__ == '__main__':
    client = ClientStartStopPage()
    client.start_client()
    time.sleep(2)
    client.load_client('123456', '123')
    time.sleep(2)
    client.close_client()
