import sys
from PyQt5.QtWidgets import *
from base.base_yaml import read_yaml,write_yaml
from PyQt5.QtCore import Qt
from base.base_path import BasePath as BP


class MainWindow(QMainWindow):
    def __init__(self, data):
        super(QMainWindow, self).__init__()
        tbar = self.addToolBar('Driver')
        submit_act = QAction('提交', self)
        select_all = QAction('全选', self)
        select_all_cancel = QAction('取消全选', self)
        submit_act.triggered.connect(self.go)
        select_all.triggered.connect(self.select_all)
        select_all_cancel.triggered.connect(self.select_all_cancel)
        tbar.addActions([submit_act, select_all, select_all_cancel])
        self.root_list = []
        w = QWidget()
        self.setCentralWidget(w)
        self.topFiller = QWidget()
        self.tree = QTreeWidget()
        # self.setCentralWidget(self.tree)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['用例名称', '用例函数'])
        self.tree.setColumnWidth(0,400)
        self.tree.clicked.connect(self.select_child)
        for i, k in enumerate(data):
            root = QTreeWidgetItem(self.tree)
            root.setText(0,data[k]['comment'])
            root.setCheckState(0, Qt.Checked)
            self.root_list.append((root, k))
            for v in data[k]:
                if v == "comment":
                    continue
                checkbox_child = QTreeWidgetItem(root)
                checkbox_child.setText(0, data[k][v])
                checkbox_child.setText(1, v)
                checkbox_child.setCheckState(0, Qt.Checked)
        self.tree.itemChanged.connect(self.select_child)
        ##创建一个滚动条
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.tree)
        self.tree.setMinimumSize(800, 800)  #######设置滚动条的尺寸
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.scroll)
        w.setLayout(self.vbox)
        self.statusBar().showMessage("Star*")
        self.resize(600, 800)
        # self.tree.expandAll()

    @staticmethod
    def select_child(*args):
        if len(args) != 2:
            return
        item, column = args
        count = item.childCount()
        if item.checkState(column) == Qt.Checked:
            for f in range(count):
                if item.child(f).checkState(0) != Qt.Checked:
                    item.child(f).setCheckState(0, Qt.Checked)
        if item.checkState(column) == Qt.Unchecked:
            for f in range(count):
                if item.child(f).checkState != Qt.Unchecked:
                    item.child(f).setCheckState(0, Qt.Unchecked)

    def select_all(self):
        for item, value in self.root_list:
            item.setCheckState(0, Qt.Checked)

    def select_all_cancel(self):
        for item, value in self.root_list:
            item.setCheckState(0, Qt.Unchecked)

    def go(self):
        select = {}
        for item, value in self.root_list:
            child_count = item.childCount()
            select[value] = []
            for f in range(child_count):
                if item.child(f).checkState(0) == Qt.Checked:
                    select[value].append(item.child(f).text(1))
            if not select[value]:
                del select[value]
        write_yaml(BP.TEST_CASES,select)


def run():
    data = read_yaml(BP.TEMP_CASES)
    app = QApplication(sys.argv)
    main_window = MainWindow(data)
    main_window.setWindowTitle('自动化测试用例执行程序')
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

