import logging
import time
import os
from base.base_path import BasePath as BP
from base.utils import read_config_ini

config = read_config_ini(BP.CONFIG_FILE)['日志打印配置']
log_time = time.strftime('%Y%m%d-%H-%M-%S', time.localtime(time.time())) + '.log'


class Logger(object):

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(config['level'])
        self.streamHandler = logging.StreamHandler()
        self.fileHandler = logging.FileHandler(os.path.join(BP.LOG_DIR,log_time), 'a', encoding='utf-8')
        self.formatter = logging.Formatter(config['formatter'])
        self.streamHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)
        self.streamHandler.setLevel(config['stream_handle_level'])
        self.fileHandler.setLevel(config['file_handle_level'])
        self.logger.addHandler(self.streamHandler)
        self.logger.addHandler(self.fileHandler)

    def get_logger(self):
        return self.logger
