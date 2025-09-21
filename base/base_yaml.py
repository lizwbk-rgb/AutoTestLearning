import yaml
import os


def read_yaml(path):  #读取yaml文件
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} 路径不存在')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def write_yaml(path, data):  #写入yaml文件
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)


if __name__ == "__main__":
    # Data = ExcelWrite()
    # filepath = r"./excelFile.xls"
    # l = [{'姓名': '张三', '年龄': 18, '职业': '学生'},
    #      {'姓名': '李四', '年龄': 19, '职业': '学生'},
    #      {'姓名': '王五', '年龄': 20, '职业': '学生'}]
    # Data.excl_write(l, filepath)
    path = r'C:\Users\v_zhquanli\PycharmProjects\AutoTestLearning\data\data_driver\yaml_driver\test.yaml'
    data = read_yaml(path)
    print(data)
