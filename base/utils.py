import os
import zipfile
from configparser import RawConfigParser


def read_config_ini(config_path):  #读取配置
    _config = RawConfigParser()
    _config.read(config_path, encoding='utf-8')
    return _config  #返回对象数据，通过字典形式读取数据


def make_zip(local_path, pack_name):
    zip_file = zipfile.ZipFile(local_path, 'w', zipfile.ZIP_DEFLATED)
    pro_len = len(os.path.dirname(local_path))
    for dir_path, dir_names, file_names in os.walk(local_path):
        for file in file_names:
            file_path = os.path.join(dir_path, file)
            arc_name = file_path[pro_len:].strip(os.path.sep)
            zip_file.write(file_path, arc_name)
    zip_file.close()
    return pack_name


def delete_all_file(path):
    for file_name in os.listdir(path):
        os.unlink(os.path.join(path, file_name))
