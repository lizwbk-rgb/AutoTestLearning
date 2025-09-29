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
