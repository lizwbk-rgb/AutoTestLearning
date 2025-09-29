import time
import pytest
from page_object.student_management_system.client_start_stop import ClientStartStopPage


@pytest.fixture(scope='function')
def client():
    client = ClientStartStopPage()
    client.start_client()
    yield
    client.close_client()
    time.sleep(1)
