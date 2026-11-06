# 导入必要的库
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, \
    QListWidget, QListWidgetItem, QScrollBar, QMessageBox
from PyQt5.QtCore import Qt
import json


class JsonFileReader(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化UI组件
        self.initUI()

        # 读取JSON文件
        self.load_json_data()

        # 设置初始状态
        self.sort_order = 'asc'
        self.search_keyword = ''
        self.selected_items = []

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建顶部按钮布局
        top_buttons_layout = QHBoxLayout()
        self.asc_button = QPushButton('升序')
        self.desc_button = QPushButton('降序')
        top_buttons_layout.addWidget(self.asc_button)
        top_buttons_layout.addWidget(self.desc_button)
        main_layout.addLayout(top_buttons_layout)

        # 创建搜索框布局
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜包含任一关键字，空格分隔')
        self.clear_button = QPushButton('清除条件')
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.clear_button)
        main_layout.addLayout(search_layout)

        # 创建全选和反选按钮布局
        select_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton('全选')
        self.deselect_all_button = QPushButton('反选')
        select_buttons_layout.addWidget(self.select_all_button)
        select_buttons_layout.addWidget(self.deselect_all_button)
        main_layout.addLayout(select_buttons_layout)

        # 创建列表显示区域
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.NoSelection)
        main_layout.addWidget(self.list_widget)

        # 创建底部状态栏布局
        bottom_status_layout = QHBoxLayout()
        self.selected_count_label = QLabel('已勾选::0')
        self.confirm_button = QPushButton('确定')
        self.cancel_button = QPushButton('取消')
        bottom_status_layout.addWidget(self.selected_count_label)
        bottom_status_layout.addWidget(self.confirm_button)
        bottom_status_layout.addWidget(self.cancel_button)
        main_layout.addLayout(bottom_status_layout)

        # 设置主布局
        self.setLayout(main_layout)

        # 连接信号与槽
        self.asc_button.clicked.connect(self.sort_asc)
        self.desc_button.clicked.connect(self.sort_desc)
        self.search_input.returnPressed.connect(self.search_items)
        self.clear_button.clicked.connect(self.clear_search)
        self.select_all_button.clicked.connect(self.select_all)
        self.deselect_all_button.clicked.connect(self.deselect_all)
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.cancel_button.clicked.connect(self.close)

        # 设置窗口属性
        self.setWindowTitle('JSON File Reader')
        self.setGeometry(300, 300, 600, 400)

    def load_json_data(self):
        try:
            with open(r'./temp/temp.json', 'r') as file:
                data = json.load(file)
                self.excel_content = data.get('excel_content', [])
                self.select_all_button.setText(f'全选({len(self.excel_content)})')
                self.display_items(self.excel_content)
        except FileNotFoundError:
            QMessageBox.warning(self, '警告', '找不到指定的JSON文件！')

    def display_items(self, items):
        self.list_widget.clear()
        for item in items:
            checkbox = QCheckBox(item)
            checkbox.stateChanged.connect(self.update_selected_count)
            list_item = QListWidgetItem()
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, checkbox)
        self.update_selected_count()

    def sort_asc(self):
        self.sort_order = 'asc'
        sorted_items = sorted(self.excel_content)
        self.display_items(sorted_items)

    def sort_desc(self):
        self.sort_order = 'desc'
        sorted_items = sorted(self.excel_content, reverse=True)
        self.display_items(sorted_items)

    def search_items(self):
        self.search_keyword = self.search_input.text().strip()
        if self.search_keyword:
            keywords = self.search_keyword.split()
            filtered_items = []
            for item in self.excel_content:
                # 包含任一关键字即匹配
                if any(keyword in item for keyword in keywords):
                    filtered_items.append(item)
            self.display_items(filtered_items)
        else:
            self.clear_search()

    def clear_search(self):
        self.search_keyword = ''
        self.search_input.clear()
        if self.sort_order == 'asc':
            self.sort_asc()
        else:
            self.sort_desc()

    def select_all(self):
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            checkbox.setChecked(True)
        self.update_selected_count()

    def deselect_all(self):
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            checkbox.setChecked(False)
        self.update_selected_count()

    def update_selected_count(self):
        count = sum(1 for i in range(self.list_widget.count()) if
                    self.list_widget.itemWidget(self.list_widget.item(i)).isChecked())
        self.selected_count_label.setText(f'已勾选::{count}')

    def confirm_selection(self):
        self.selected_items = [self.list_widget.itemWidget(self.list_widget.item(i)).text() for i in
                               range(self.list_widget.count()) if
                               self.list_widget.itemWidget(self.list_widget.item(i)).isChecked()]
        QMessageBox.information(self, '确认',
                                f'已选择 {len(self.selected_items)} 项：\n{", ".join(self.selected_items)}')
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    window = JsonFileReader()
    window.show()
    app.exec_()