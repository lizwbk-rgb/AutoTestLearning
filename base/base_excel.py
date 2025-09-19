import xlrd
import xlwt


class ExcelRead(object):
    def __init__(self, excel_path, sheet_name="Sheet1"):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheet_by_name(sheet_name)
        self.keys = self.table.row_values(0)  #读取第一行的key值
        self.rowNum = self.table.nrows  #获取总行数
        self.colNum = self.table.ncols  #获取总列数

    def dict_data(self):  #读取表格内全部的数据[{}]
        if self.rowNum <= 1:
            print("总行数小于等于1")
        else:
            test_data = []
            key = 1
            for i in range(self.rowNum - 1):
                data_item = {}
                value = self.table.row_values(key)
                key = key + 1
                for x in range(self.colNum):
                    data_item[x] = value[x]
                test_data.append(data_item)
            return test_data

    def get_row_info(self, row):  #读取表格内行的数据
        if self.rowNum <= 1:
            row_data = None
        else:
            test_data = self.dict_data()
            row_data = test_data[row - 2]
        return row_data

    def get_col_info(self, name):  #读取表格中列的信息
        col_data = []
        test_data = self.dict_data()
        for data in test_data:
            col_data.append(data[name])
        return col_data

    def get_cell_info(self, row, col):  #读取表格中单元格的信息
        if self.rowNum <= 1:
            cell_data = None
        else:
            test_data = self.dict_data()
            cell_data = test_data[row - 2][col]
        return cell_data


class ExcelWrite(object):
    def __init__(self, sheet_name="Sheet1"):
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.worksheet = self.workbook.add_sheet(sheet_name)

    def set_header(self, list_data):  #设置数据标题
        if not isinstance(list_data, list):
            raise TypeError("数据必须是列表")
        key_data = list(set(list_data[0].keys()))
        num = len(key_data)
        for cell in range(num):
            self.worksheet.write(0, cell, label=key_data[cell])

    def write_excl(self, list_data, excel_path):  #写入数据
        if not isinstance(list_data, list):
            raise TypeError("数据必须是列表")
        self.set_header(list_data)
        row_num = len(list_data)
        for row in range(row_num):
            value = list(list_data[row].values())
            col_num = len(value)
            for col in range(col_num):
                self.worksheet.write(row + 1, col, value[col])
        self.workbook.save(excel_path)


if __name__ == "__main__":
    # Data = ExcelWrite()
    # filepath = r"./excelFile.xls"
    # l = [{'姓名': '张三', '年龄': 18, '职业': '学生'},
    #      {'姓名': '李四', '年龄': 19, '职业': '学生'},
    #      {'姓名': '王五', '年龄': 20, '职业': '学生'}]
    # Data.excl_write(l, filepath)
    path = r'C:\Users\v_zhquanli\PycharmProjects\AutoTestLearning\data\data_driver\yaml_driver\test.yaml'
    data = read_
    print(col)
