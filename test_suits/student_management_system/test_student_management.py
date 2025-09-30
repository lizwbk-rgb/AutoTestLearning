import pytest
from base.base_data import DataDriver
from page_object.student_management_system.client_start_stop import ClientStartStopPage


class TestLogin:
    """登录类"""

    @pytest.mark.parametrize('login_data', DataDriver().get_case_data('login'))
    @pytest.mark.usefixtures('client')
    def test_01(self, login_data):
        """登录测试"""
        client = ClientStartStopPage()
        client.load_client(login_data['username'], login_data['password'])
        client.assert_login(login_data['flag'])

    @pytest.mark.parametrize('register_data', DataDriver().get_case_data('register'))
    @pytest.mark.usefixtures('client')
    def test_02(self, register_data):
        """注册测试"""
        client = ClientStartStopPage()
        client.register(register_data['username'], register_data['age'],
                        register_data['user_id'], register_data['password'])
