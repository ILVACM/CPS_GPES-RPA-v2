#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI JSON列表选择器模块
通过PyQt5实现的图形界面，用于从JSON文件中选择指定键的列表项

依赖库:
- PyQt5: 用于创建图形用户界面
- json: 用于解析JSON文件
- os: 用于检查文件是否存在
"""

import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, \
    QListWidget, QListWidgetItem, QMessageBox
import sys


class JsonFileReader(QWidget):
    """
    JSON文件读取器窗口类
    提供图形界面用于从JSON文件中选择指定键的列表项
    """
    def __init__(self, json_file_path, key_name):
        """
        初始化窗口
        
        参数:
            json_file_path (str): JSON文件路径
            key_name (str): 需要读取的键名
        """
        super().__init__()
        
        # 存储参数
        self.json_file_path = json_file_path
        self.key_name = key_name
        self.result = None

        # 初始化UI组件
        self.initUI()

        # 读取JSON文件
        self.load_json_data()

        # 设置初始状态
        self.sort_order = 'asc'
        self.search_keyword = []
        self.selected_items = []

    def initUI(self):
        """
        初始化用户界面
        """
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
        self.cancel_button.clicked.connect(self.cancel_operation)

        # 设置窗口属性
        self.setWindowTitle('JSON File Reader')
        self.setGeometry(300, 300, 600, 400)

    def load_json_data(self):
        """
        从JSON文件加载数据
        """
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.excel_content = data.get(self.key_name, [])
                self.select_all_button.setText(f'全选({len(self.excel_content)})')
                self.display_items(self.excel_content)
        except FileNotFoundError:
            QMessageBox.warning(self, '警告', f'找不到指定的JSON文件：{self.json_file_path}！')

    def display_items(self, items):
        """
        在列表中显示项目
        
        参数:
            items (list): 要显示的项目列表
        """
        self.list_widget.clear()
        for item in items:
            checkbox = QCheckBox(item)
            checkbox.stateChanged.connect(self.update_selected_count)
            list_item = QListWidgetItem()
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, checkbox)
        self.update_selected_count()

    def sort_asc(self):
        """
        按升序排序
        """
        self.sort_order = 'asc'
        sorted_items = sorted(self.excel_content)
        self.display_items(sorted_items)

    def sort_desc(self):
        """
        按降序排序
        """
        self.sort_order = 'desc'
        sorted_items = sorted(self.excel_content, reverse=True)
        self.display_items(sorted_items)

    def search_items(self):
        """
        搜索项目
        """
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
        """
        清除搜索条件
        """
        self.search_keyword = ''
        self.search_input.clear()
        if self.sort_order == 'asc':
            self.sort_asc()
        else:
            self.sort_desc()

    def select_all(self):
        """
        全选所有项目
        """
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            checkbox.setChecked(True)
        self.update_selected_count()

    def deselect_all(self):
        """
        取消选择所有项目
        """
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            checkbox.setChecked(False)
        self.update_selected_count()

    def update_selected_count(self):
        """
        更新已选择项目计数
        """
        count = sum(1 for i in range(self.list_widget.count()) if
                    self.list_widget.itemWidget(self.list_widget.item(i)).isChecked())
        self.selected_count_label.setText(f'已勾选::{count}')

    def confirm_selection(self):
        """
        确认选择操作
        """
        self.selected_items = [self.list_widget.itemWidget(self.list_widget.item(i)).text() for i in
                               range(self.list_widget.count()) if
                               self.list_widget.itemWidget(self.list_widget.item(i)).isChecked()]
        self.result = self.selected_items
        print(f" *** 总计-{len(self.selected_items)}-元素::{self.selected_items} ")
        self.close()
        
    def cancel_operation(self):
        """
        取消操作
        """
        self.result = None
        print(" *** 取消操作 ")
        self.close()
        
    def get_result(self):
        """
        获取选择结果
        
        返回:
            list or None: 选中的项目列表，如果取消则返回None
        """
        return self.result

def GUI_JSON_list_selector(json_file_path, key_name):
    """
    GUI JSON列表选择器函数
    通过图形界面从JSON文件中选择指定键的列表项
    
    参数:
        json_file_path (str): JSON文件路径（支持相对路径和绝对路径）
        key_name (str): 需要读取的键名
        
    返回:
        list or None: 用户选择的项目列表，如果用户取消则返回None
        
    异常:
        ValueError: 当参数为空时抛出
        FileNotFoundError: 当文件不存在时抛出
    """
    try:
        # 1. 初始化+检查
        # 检查参数输入
        if not json_file_path:
            print(" *** 参数检查:失败 - JSON文件路径为空")
            raise ValueError("JSON文件路径不能为空")
        print(" *** 参数检查:成功 - JSON文件路径检查通过")
        
        if not key_name:
            print(" *** 参数检查:失败 - 键名为空")
            raise ValueError("键名不能为空")
        print(" *** 参数检查:成功 - 键名检查通过")
        
        # 检查目标文件是否存在
        if not os.path.exists(json_file_path):
            print(f" *** 文件检查:失败 - 文件 {json_file_path} 不存在")
            raise FileNotFoundError(f"文件 {json_file_path} 不存在")
        print(f" *** 文件检查:成功 - 文件 {json_file_path} 存在")
        
        # 初始化结果列表
        result_list = []
        print(" *** 初始化:成功 - 结果列表初始化完成")
        
        # 2. 创建并运行GUI界面
        # 检查是否已存在QApplication实例
        app = QApplication.instance()
        if app is None:
            # 如果没有则创建新的QApplication实例
            app = QApplication(sys.argv)
        
        # 创建窗口实例
        window = JsonFileReader(json_file_path, key_name)
        window.show()
        
        # 运行事件循环
        app.exec_()
        
        # 3. 获取并返回结果
        result = window.get_result()
        return result
        
    except Exception as e:
        # 捕获并重新抛出异常
        print(f" *** 错误: {str(e)}")
        raise


if __name__ == '__main__':
    # 示例用法
    try:
        selected_items = GUI_JSON_list_selector('../temp/temp.json', 'excel_content')
        if selected_items is not None:
            print(f"选中的项目: {selected_items}")
        else:
            print("操作已取消")
    except Exception as e:
        print(f"程序执行出错: {e}")
