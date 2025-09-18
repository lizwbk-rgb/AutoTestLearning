from configparser import RawConfigParser


def read_config_ini(config_path):  #读取配置
    _config = RawConfigParser()
    _config.read(config_path, encoding='utf-8')
    return _config  #返回对象数据，通过字典形式读取数据
