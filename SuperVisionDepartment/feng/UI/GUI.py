# -*- coding: utf-8 -*-
"""
通过PyQt5构建GUI，让用户选择Excel文件的表头行。
"""

import sys
import os
import json

import logging
from typing import Optional, Union

# 删除原有的日志配置，使用主程序中的日志设置
# 配置日志记录器
# logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 尝试导入所需的库
try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QRadioButton, QScrollArea, QPushButton, QLabel,
        QMessageBox, QButtonGroup, QFrame
    )

    from PyQt5.QtWidgets import (
        QLineEdit, QCheckBox, QListWidget, QListWidgetItem
    )

    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFontMetrics

    # logger.info(" *** PyQt5:Check 成功 ")
except ImportError as e:
    # logger.error(" *** PyQt5:Check 失败 ||-||-|| 未安装或导入失败: %s", e)
    raise

try:
    from openpyxl import load_workbook

    # logger.info(" *** openpyxl:Check 成功 ")
except ImportError as e:
    # logger.error(" *** openpyxl:Check 失败 ||-||-|| 未安装或导入失败: %s", e)
    raise


def GUI_JSON_list_selector(json_file_path, key_name, window_title=None):
    """
    GUI JSON列表选择器函数
    通过图形界面从JSON文件中选择指定键的列表项

    参数:
        json_file_path (str): JSON文件路径（支持相对路径和绝对路径）
        key_name (str): 需要读取的键名
        window_title (str, optional): 窗口标题，如果为空则使用默认标题"GUI_JSON_Selector"

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
        window = JsonFileReader(json_file_path, key_name, window_title)
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


class JsonFileReader(QWidget):
    """
    JSON文件读取器窗口类
    提供图形界面用于从JSON文件中选择指定键的列表项
    """

    def __init__(self, json_file_path, key_name, window_title=None):
        """
        初始化窗口

        参数:
            json_file_path (str): JSON文件路径
            key_name (str): 需要读取的键名
            window_title (str, optional): 窗口标题，如果为空则使用默认标题"GUI_JSON_Selector"
        """
        super().__init__()

        # 存储参数
        self.json_file_path = json_file_path
        self.key_name = key_name
        self.result = None

        # 处理窗口标题参数
        if not window_title or not isinstance(window_title, str):
            self.window_title = "GUI_JSON_Selector"
        else:
            self.window_title = window_title

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
        self.setWindowTitle(self.window_title)
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
        # 存储原始项目数据，用于后续返回
        self.original_items = items
        for i, item in enumerate(items):
            # 显示时转换为字符串，但保持原始数据引用
            item_text = item if isinstance(item, str) else str(item)
            checkbox = QCheckBox(item_text)
            checkbox.stateChanged.connect(self.update_selected_count)
            list_item = QListWidgetItem()
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, checkbox)
            # 将原始数据索引存储在checkbox的属性中
            checkbox.setProperty('original_index', i)
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
        # 获取原始数据而不是显示文本
        selected_original_items = []
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            if checkbox.isChecked():
                # 通过索引获取原始数据
                original_index = checkbox.property('original_index')
                selected_original_items.append(self.original_items[original_index])

        self.result = selected_original_items
        print(f" *** 总计-{len(self.result)}-元素::{self.result} ")
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


"""
本模块提供一个基于PyQt5的图形界面函数
"""


def excel_head_row_GUI_select(file_path: str, sheet_name: str = "") -> Optional[int]:
    """
    通过GUI界面让用户选择Excel文件的表头行。

    此函数会读取指定Excel文件的前10行数据，并在一个带有滚动条的PyQt5窗口中显示，
    用户可以通过单选按钮选择其中一行作为表头行。用户确认选择后，函数返回所选行的序号（从1开始）；
    如果用户取消操作，则返回None。

    参数:
        file_path (str): Excel文件的路径（相对或绝对路径）。
        sheet_name (str, optional): 要读取的工作表名称。如果为空或None，则读取第一个工作表。

    返回:
        Optional[int]: 用户选择的行号（1-based），如果用户取消则返回None。

    异常:
        ValueError: 如果file_path为空或文件不存在。
        Exception: 其他在读取文件或创建GUI时发生的错误。
    """
    logger.info(" *** 函数调用:Init 开始 ")

    # --- 1. 初始化+检查 ---
    logger.info(" *** 参数检查与初始化:Check 开始 ")
    if not file_path:
        logger.error(" *** 参数检查:Check 失败 ||-||-|| file_path不能为空")
        raise ValueError("file_path不能为空")
    if not os.path.exists(file_path):
        logger.error(" *** 参数检查:Check 失败 ||-||-|| 文件不存在: %s", file_path)
        raise ValueError(f"文件不存在: {file_path}")
    logger.info(" *** file_path参数检查:Check 成功 ")

    # --- 2. 读取Excel数据 ---
    logger.info(" *** Excel文件读取:Init 开始 ")
    try:
        workbook = load_workbook(filename=file_path, read_only=True, data_only=True)
        logger.info(" *** Excel文件读取:Init 成功 ")

        logger.info(" *** 工作表检查与选择:Check 开始 ")
        if not sheet_name or sheet_name not in workbook.sheetnames:
            # 如果sheet_name为空或不存在，则使用第一个工作表
            original_sheet_name = sheet_name
            sheet_name = workbook.sheetnames[0]
            logger.info(" *** 工作表检查:Check |-> 原始输入: '%s' ||-||-|| 使用默认: '%s' ||-||-|| 成功 ",
                        original_sheet_name, sheet_name)
        else:
            logger.info(" *** sheet_name参数检查:Check 成功 ")

        worksheet = workbook[sheet_name]

        logger.info(" *** 数据读取:Init 开始 ")
        # 读取前10行数据
        data_rows = []
        for i, row in enumerate(worksheet.iter_rows(min_row=1, max_row=10, values_only=True), start=1):
            # 处理可能的None值，确保可以转换为字符串显示
            processed_row = [str(cell) if cell is not None else "" for cell in row]
            data_rows.append(processed_row)
            logger.info(f" *** 读取第{i}行数据: {processed_row}")

        if not data_rows:
            logger.warning(" *** 数据读取:Init 完成 ||-||-|| 未读取到任何数据行 ")
        else:
            logger.info(" *** 数据读取:Init 成功 ")

    except Exception as e:
        logger.error(" *** Excel文件读取/数据读取:Init 失败 ||-||-|| 错误: %s", e)
        raise

    # --- 3. 创建并运行GUI ---
    logger.info(" *** GUI应用启动:Init 开始 ")
    app = QApplication.instance()  # 检查是否已存在QApplication实例
    if app is None:
        app = QApplication(sys.argv)
        logger.info(" *** 创建新的QApplication实例:Init 成功 ")
    else:
        logger.info(" *** 使用已存在的QApplication实例:Init 成功 ")

    logger.info(" *** GUI窗口组件创建:Init 开始 ")
    selector_window = ExcelRowSelectorGUI(data_rows)
    logger.info(" *** GUI窗口组件创建:Init 成功 ")

    logger.info(" *** GUI窗口显示:Init 开始 ")
    selector_window.show()
    logger.info(" *** GUI窗口显示:Init 成功 ")

    logger.info(" *** GUI事件循环启动:Init 开始 ")
    # 运行GUI并等待其关闭
    app.exec_()
    logger.info(" *** GUI事件循环结束:Init 成功 ")

    # 获取并返回结果
    selected_row = selector_window.get_selected_row()
    if selected_row is not None:
        logger.info(" *** 用户选择结果: %d ", selected_row)
    else:
        logger.info(" *** 用户取消操作或未选择 ")
    return selected_row


class ExcelRowSelectorGUI(QWidget):
    """
    自定义的PyQt5窗口类，用于显示Excel行数据并供用户选择。
    """

    def __init__(self, data_rows):
        """
        初始化GUI窗口。

        参数:
            data_rows (list of list): 从Excel读取的前N行数据，每个子列表代表一行。
        """
        super().__init__()
        self.data_rows = data_rows
        self.selected_row_index = None  # 0-based index
        self.init_ui()

    def init_ui(self):
        """设置窗口的UI布局和组件。"""
        self.setWindowTitle('选择Excel表头行')
        self.resize(800, 400)  # 设置初始窗口大小

        # --- 主要内容区 (垂直布局) ---
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 创建一个滚动区域用于容纳单选按钮列表
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 允许内部widget调整大小
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)

        # 在滚动区域的widget内创建垂直布局放置单选按钮
        self.radio_layout = QVBoxLayout()
        self.radio_layout.setAlignment(Qt.AlignTop)  # 将内容对齐到顶部
        self.scroll_widget.setLayout(self.radio_layout)

        # 使用QButtonGroup管理单选按钮互斥
        self.button_group = QButtonGroup()
        self.radio_buttons = []

        # 根据读取的数据创建单选按钮和行显示
        for i, row_data in enumerate(self.data_rows):
            # 创建一个水平布局来放置单选按钮和行数据标签
            h_layout = QHBoxLayout()

            radio_button = QRadioButton()
            self.button_group.addButton(radio_button, i)  # 将按钮和其索引(0-based)添加到组中
            self.radio_buttons.append(radio_button)

            # --- 修改部分：使用QFrame和QLabel实现左对齐 ---
            # 创建一个框架来包裹行数据，便于设置样式和对齐
            row_frame = QFrame()
            row_frame.setFrameShape(QFrame.StyledPanel)  # 可视化边界
            row_frame_layout = QHBoxLayout()
            row_frame_layout.setContentsMargins(5, 2, 5, 2)  # 减小内部边距
            row_frame.setLayout(row_frame_layout)

            # 创建一个标签来显示行数据
            row_text = '\t'.join(row_data)
            row_label = QLabel(row_text)
            # 设置标签文本左对齐
            row_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            # 如果文本很长，可能需要设置自动换行或省略，这里简单处理
            # row_label.setWordWrap(True) # 可选：允许文本换行
            # row_label.setTextFormat(Qt.PlainText) # 确保特殊字符被正确显示

            row_frame_layout.addWidget(row_label)
            # --- 修改结束 ---

            h_layout.addWidget(radio_button)
            # 将框架添加到水平布局中
            h_layout.addWidget(row_frame, 1)  # stretch=1 使其占据剩余空间
            # 将这个水平布局添加到主滚动区域的垂直布局中
            self.radio_layout.addLayout(h_layout)

        # 连接按钮组的信号，当按钮被选中时更新显示
        self.button_group.buttonClicked[int].connect(self.on_radio_button_selected)

        main_layout.addWidget(self.scroll_area)

        # --- 底部操作区 ---
        bottom_layout = QHBoxLayout()

        # 显示当前选中行号的标签
        self.selected_label = QLabel("点选行序列::")
        bottom_layout.addWidget(self.selected_label)

        # 添加弹性空间将按钮推到右侧
        bottom_layout.addStretch()

        # 确定按钮
        self.ok_button = QPushButton('确定')
        self.ok_button.clicked.connect(self.on_ok_clicked)
        bottom_layout.addWidget(self.ok_button)

        # 取消按钮
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        bottom_layout.addWidget(self.cancel_button)

        main_layout.addLayout(bottom_layout)

    def on_radio_button_selected(self, button_id: int):
        """
        当单选按钮被点击时的槽函数。
        更新选中行号的显示。
        """
        self.selected_row_index = button_id
        self.selected_label.setText(f"点选行序列::{self.selected_row_index + 1}")  # 转换为1-based显示

    def on_ok_clicked(self):
        """
        当“确定”按钮被点击时的槽函数。
        检查是否有选择，然后关闭窗口。
        """
        if self.selected_row_index is None:
            QMessageBox.warning(self, "未选择", "请先选择一行数据。")
            return
        # self.selected_row_index 是 0-based，直接关闭窗口，get_selected_row会处理转换
        self.close()

    def on_cancel_clicked(self):
        """
        当“取消”按钮被点击时的槽函数。
        清除选择并关闭窗口。
        """
        self.selected_row_index = None
        self.close()

    def get_selected_row(self) -> Optional[int]:
        """
        获取用户选择的行号。

        返回:
            Optional[int]: 用户选择的行号（1-based），如果未选择或取消则返回None。
        """
        if self.selected_row_index is not None:
            return self.selected_row_index + 1  # 转换为1-based序号
        return None


"""
本模块提供一个基于PyQt5的图形界面函数，用于对Excel文件进行多表头条件匹配筛选。
"""

# 配置日志（示例，实际使用时应由主程序配置）
# logging.basicConfig(level=logging.INFO, format='%(message)s')

import sys
import os
# import json  # 函数签名提到了json，但当前实现未使用
import pandas as pd
from openpyxl import Workbook, load_workbook
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTableView, QLabel, QMessageBox, QScrollArea, QFrame, QDialog
)


def GUI_XLSX_export_MultiCondition(
        src_file_path: str,
        src_sheet_names: list,
        header_conditions: list,
        dst_file_path: str,
        dst_sheet_name: str):
    """
    创建一个GUI界面，用于根据多表头条件筛选Excel数据并导出。

    :param src_file_path: 源Excel文件路径（绝对或相对）。
    :param src_sheet_names: 要读取的源数据表名称列表。
    :param header_conditions: 用于匹配的表头条件列表。
    :param dst_file_path: 目标Excel文件路径。
    :param dst_sheet_name: 目标数据表名称。
    :return: 成功时返回目标文件路径，失败或取消时返回None。
    """

    try:
        print(f" *** 参数检查与初始化: 开始")

        # --- 1. 初始化+检查 ---
        if not src_file_path or not isinstance(src_file_path, str):
            raise ValueError("源文件路径不能为空")
        if not os.path.exists(src_file_path):
            raise FileNotFoundError(f"源文件不存在: {src_file_path}")
        print(f" *** 源文件路径检查: '{src_file_path}' ||-||-|| 成功 ")

        if not src_sheet_names or not isinstance(src_sheet_names, list):
            print(f" *** 源数据表名列表为空 |-> 将使用默认第一个工作表 ||-||-|| 成功 ")
            src_sheet_names = None  # 标记为None，后续处理

        if not header_conditions or not isinstance(header_conditions, list):
            print(f" *** 表头筛选条件列表为空 |-> 将筛选所有表头 ||-||-|| 成功 ")
            header_conditions = None  # 标记为None，后续处理

        if not dst_file_path or not isinstance(dst_file_path, str):
            raise ValueError("目标文件路径不能为空")
        print(f" *** 目标文件路径检查: '{dst_file_path}' ||-||-|| 成功 ")

        # 确定目标Sheet名称
        final_dst_sheet_name = "Sheet1"
        if dst_sheet_name and isinstance(dst_sheet_name, str):
            final_dst_sheet_name = dst_sheet_name
        else:
            print(f" *** 目标数据表名为空 |-> 默认使用 'Sheet1' ||-||-|| 成功 ")

        print(f" *** 参数检查与初始化: 完成 ")

        # --- 2. 读取和处理Excel源文件 ---
        print(f" *** 读取源文件: 开始")
        df_dict = pd.read_excel(src_file_path, sheet_name=None)  # 读取所有sheet
        available_sheets = list(df_dict.keys())
        print(f" *** 读取源文件: 发现 {len(available_sheets)} 个工作表 ||-||-|| 成功 ")

        sheets_to_process = []
        if src_sheet_names is None:
            # 如果未指定，则处理第一个可用的工作表
            if available_sheets:
                sheets_to_process.append(available_sheets[0])
                print(f" *** 未指定源数据表 |-> 使用第一个工作表 '{sheets_to_process[0]}' ||-||-|| 成功 ")
            else:
                raise ValueError("源Excel文件中没有找到任何工作表")
        else:
            for name in src_sheet_names:
                if name in available_sheets:
                    sheets_to_process.append(name)
                else:
                    print(f" *** 请求的工作表 '{name}' 不存在于源文件中，已跳过.")

        if not sheets_to_process:
            raise ValueError("没有有效的源数据表可供处理")

        # 存储每个工作表的结果DataFrame
        results_per_sheet = {}

        app = QApplication.instance()  # 检查是否已有QApplication实例
        if app is None:
            app = QApplication(sys.argv)

        all_success = True
        for sheet_name in sheets_to_process:
            df_original = df_dict[sheet_name]

            # 2.2 确定筛选依据的表头
            headers_in_df = df_original.columns.tolist()

            matched_headers = []
            if header_conditions is None:
                # 如果未指定条件，则所有表头都匹配
                matched_headers = headers_in_df[:]
            else:
                # 否则进行严格匹配
                for cond in header_conditions:
                    stripped_cond = cond.strip()  # 清除首尾无效空格
                    if stripped_cond in headers_in_df:
                        matched_headers.append(stripped_cond)

            if not matched_headers:
                print(f" *** 警告: 工作表 '{sheet_name}' 中未找到任何匹配的表头。将处理所有列。")
                matched_headers = headers_in_df[:]  # Fallback

            print(f" *** {os.path.basename(src_file_path)}::{sheet_name} |-> {matched_headers}")

            # 运行GUI并获取结果
            gui_app = ExcelFilterApp(df_original.copy(), matched_headers, sheet_name)
            result_code = gui_app.exec_()

            if result_code == 1:  # 用户点击了“确定”
                filtered_df = gui_app.get_filtered_data()
                results_per_sheet[sheet_name] = filtered_df
                num_rows = len(filtered_df)
                print(
                    f" *#* {os.path.basename(src_file_path)}::{sheet_name} ==> {num_rows} 行.合法 -> {os.path.basename(dst_file_path)}::{final_dst_sheet_name}_{sheet_name}")
            else:  # 用户点击了“取消”或其他情况
                print(f" *** 用户取消了对工作表 '{sheet_name}' 的操作。")
                all_success = False
                break

        if not all_success:
            return None

        # --- 3. 写入结果到目标文件 ---
        print(f" *** 写入结果到目标文件: 开始")
        total_written_rows = 0

        # 确保目标目录存在
        dst_dir = os.path.dirname(dst_file_path)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            print(f" *** 创建目标文件夹: '{dst_dir}' ||-||-|| 成功 ")

        # 生成临时文件路径
        import tempfile
        temp_dir = os.path.dirname(dst_file_path) if os.path.dirname(dst_file_path) else '.'
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', dir=temp_dir, delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # 使用临时文件写入数据
            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                for i, (orig_sheet_name, df_result) in enumerate(results_per_sheet.items()):
                    current_sheet_name = f"{final_dst_sheet_name}_{orig_sheet_name}" if len(
                        sheets_to_process) > 1 else final_dst_sheet_name

                    # 确保工作表名称不超过Excel限制（31个字符）并去除非法字符
                    current_sheet_name = current_sheet_name[:31]
                    invalid_chars = ['\\', '/', '*', '[', ']', ':', '?']
                    for char in invalid_chars:
                        current_sheet_name = current_sheet_name.replace(char, '_')

                    df_result.to_excel(writer, sheet_name=current_sheet_name, index=False)
                    total_written_rows += len(df_result)
                    print(f" *** 数据写入 '{current_sheet_name}': {len(df_result)} 行 ||-||-|| 成功 ")

            # 如果目标文件已存在，先删除
            if os.path.exists(dst_file_path):
                os.remove(dst_file_path)

            # 将临时文件移动到目标位置
            os.rename(temp_path, dst_file_path)

            print(f" *** 写入结果到目标文件: 完成 ")
            print(f" >>> 当前已筛选出 {total_written_rows} 行 <<< \n ***|||*** output ==> {dst_file_path}")
            return dst_file_path

        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f" *** 错误: 写入文件时发生异常: {e}")
            return None

    except Exception as e:
        print(f" *** 错误: 在执行过程中发生异常: {e}")
        return None


class ExcelFilterApp(QDialog):
    def __init__(self, df, headers, sheet_name):
        super().__init__()
        self.df_original = df
        self.headers = headers
        self.sheet_name = sheet_name
        self.filtered_df = self.df_original.copy()
        self.conditions = {header: "" for header in self.headers}  # 初始条件为空字符串

        self.setWindowTitle(f"excel数据表筛选 - [{self.sheet_name}]")
        self.resize(1000, 700)
        self.layout = QVBoxLayout(self)

        self._setup_ui()

    def _setup_ui(self):
        # --- 顶部工具栏区域 ---
        self.toolbar_frame = QFrame()
        self.toolbar_layout = QHBoxLayout(self.toolbar_frame)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)

        # 添加弹性空间将按钮推到右侧
        self.toolbar_layout.addStretch()

        # 创建全屏化按钮
        self.fullscreen_button = QPushButton("□")  # 使用方框符号表示全屏按钮
        self.fullscreen_button.setFixedSize(30, 30)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        self.toolbar_layout.addWidget(self.fullscreen_button)

        self.layout.addWidget(self.toolbar_frame)

        # --- 表头显示区和条件设置区 ---
        self.header_condition_area = QFrame()
        self.header_condition_layout = QHBoxLayout(self.header_condition_area)
        self.header_scroll = QScrollArea()
        self.header_scroll.setWidgetResizable(True)
        self.header_scroll.setWidget(self.header_condition_area)
        self.header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layout.addWidget(self.header_scroll)

        self.header_labels = {}
        self.condition_inputs = {}
        for header in self.headers:
            # 垂直布局容纳一个表头和一个输入框
            v_layout = QVBoxLayout()
            label = QLabel(str(header))
            label.setStyleSheet("font-weight: bold; border: 1px solid gray;")
            line_edit = QLineEdit()
            line_edit.setObjectName(header)  # 设置对象名方便查找
            line_edit.returnPressed.connect(self.on_condition_changed)  # 回车触发筛选
            line_edit.textChanged.connect(lambda text, h=header: self.update_condition(h, text))  # 实时更新条件字典

            self.header_labels[header] = label
            self.condition_inputs[header] = line_edit

            v_layout.addWidget(label)
            v_layout.addWidget(line_edit)
            self.header_condition_layout.addLayout(v_layout)

        # --- 主要内容区 ---
        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        # self.table_view.setAlternatingRowColors(True) # 可选：交替行颜色
        self.layout.addWidget(self.table_view, stretch=4)  # 占据大部分空间

        # --- 底部操作区 ---
        self.bottom_frame = QFrame()
        self.bottom_layout = QHBoxLayout(self.bottom_frame)
        self.count_label = QLabel("当前数据行::0")
        self.refresh_button = QPushButton("刷新")
        self.reset_button = QPushButton("重置")
        self.confirm_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")

        self.refresh_button.clicked.connect(self.apply_filters)
        self.reset_button.clicked.connect(self.reset_filters)
        self.confirm_button.clicked.connect(self.accept)  # QDialog accept
        self.cancel_button.clicked.connect(self.reject)  # QDialog reject

        self.bottom_layout.addWidget(self.count_label)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.refresh_button)
        self.bottom_layout.addWidget(self.reset_button)
        self.bottom_layout.addWidget(self.confirm_button)
        self.bottom_layout.addWidget(self.cancel_button)
        self.layout.addWidget(self.bottom_frame)

        self.load_table_data(self.df_original)  # 初始加载原始数据

    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_button.setText("□")  # 恢复正常模式时显示方框
        else:
            self.showFullScreen()
            self.fullscreen_button.setText("❐")  # 全屏时显示恢复符号

    def update_condition(self, header, text):
        """实时更新筛选条件"""
        self.conditions[header] = text.strip()

    def on_condition_changed(self):
        """当任一输入框回车或失去焦点时应用筛选"""
        self.apply_filters()

    def apply_filters(self):
        """根据当前条件筛选数据"""
        mask = pd.Series([True] * len(self.df_original), index=self.df_original.index)
        for col, condition_text in self.conditions.items():
            if condition_text:  # 如果有条件才过滤
                # 宽松匹配：包含即可
                mask &= self.df_original[col].astype(str).str.contains(condition_text, case=False, na=False)
        self.filtered_df = self.df_original[mask]
        self.load_table_data(self.filtered_df)
        self.count_label.setText(f"当前数据行::{len(self.filtered_df)}")

    def reset_filters(self):
        """重置筛选条件"""
        for le in self.condition_inputs.values():
            le.clear()
        self.conditions = {header: "" for header in self.headers}
        self.filtered_df = self.df_original.copy()
        self.load_table_data(self.filtered_df)
        self.count_label.setText(f"当前数据行::{len(self.filtered_df)}")

    def load_table_data(self, dataframe):
        """将DataFrame加载到表格视图中"""
        self.model.clear()
        self.model.setColumnCount(len(dataframe.columns))
        self.model.setRowCount(len(dataframe.index))
        self.model.setHorizontalHeaderLabels([str(col) for col in dataframe.columns])

        for row_idx, (_, row) in enumerate(dataframe.iterrows()):
            for col_idx, value in enumerate(row):
                item = QStandardItem(str(value))
                item.setEditable(False)  # 不可编辑
                self.model.setItem(row_idx, col_idx, item)

        # 调整列宽以适应内容
        self.table_view.resizeColumnsToContents()

    def get_filtered_data(self):
        """获取最终筛选后的DataFrame"""
        return self.filtered_df.copy()


"""
基于PyQt5实现的Excel数据筛选和排序GUI工具。

该工具提供一个图形界面，允许用户加载Excel文件，设置筛选条件，
对数据进行分组和排序，并将结果导出到新的Excel文件。
"""

import sys
import os
import json
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,  # 添加 QGridLayout
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox,
    QProgressBar, QStyle
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor


def GUI_XLSX_export_MultiCondition_MultiSort(
        input_file_path,
        source_sheet_name,
        header_conditions,
        group_by_headers,
        sort_by_headers,
        output_file_path,
        output_sheet_name
):
    """
    启动一个PyQt5 GUI，用于筛选和排序Excel数据。

    :param input_file_path: str, 输入Excel文件路径 (绝对或相对)。
    :param source_sheet_name: str, 源数据表名称。如果为空，则使用第一个表。
    :param header_conditions: list, 需要解析的表头名列表。如果为空，则解析所有表头。
    :param group_by_headers: list, 用于分组的表头名列表。如果为空，则不分组。
    :param sort_by_headers: list, 用于分组内排序的表头名列表。如果为空，则不分组内排序。
    :param output_file_path: str, 输出Excel文件路径 (绝对或相对)。
    :param output_sheet_name: str, 输出数据表名称。如果为空，则使用默认名称。
    :return: str or None, 成功时返回输出文件路径，失败时返回None。
    """
    try:
        # --- 1. 初始化+检查 ---
        print(f" *** 参数检查:Check 开始 ***")

        # 1.1 检查 input_file_path
        if not input_file_path:
            raise ValueError("输入文件路径不能为空。")
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"输入文件不存在: {input_file_path}")
        print(f" *** 输入文件路径检查:Check 成功 ")

        # 1.2 处理 source_sheet_name (默认值处理在加载时进行)
        if not source_sheet_name:
            print(f" *** 源数据表名称:Init |-> 使用默认值(第一个表) ||-||-|| 成功 ")
        else:
            print(f" *** 源数据表名称:Init 成功 ")

        # 1.3 处理 header_conditions
        if not header_conditions:
            header_conditions = None  # pandas read_excel 会处理 None
            print(f" *** 表头筛选条件:Init |-> 使用默认值(所有表头) ||-||-|| 成功 ")
        else:
            print(f" *** 表头筛选条件:Init 成功 ")

        # 1.4 处理 group_by_headers
        if not group_by_headers:
            group_by_headers = []
            print(f" *** 分组条件:Init |-> 使用默认值(不分组) ||-||-|| 成功 ")
        else:
            print(f" *** 分组条件:Init 成功 ")

        # 1.5 处理 sort_by_headers
        if not sort_by_headers:
            sort_by_headers = []
            print(f" *** 分组内排序条件:Init |-> 使用默认值(不排序) ||-||-|| 成功 ")
        else:
            print(f" *** 分组内排序条件:Init 成功 ")

        # 1.6 检查 output_file_path
        if not output_file_path:
            raise ValueError("输出文件路径不能为空。")
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(f" *** 输出文件路径检查:Check 成功 ")

        # 1.7 处理 output_sheet_name (默认值处理在保存时进行)
        if not output_sheet_name:
            print(f" *** 输出数据表名称:Init |-> 使用默认值(Sheet1/Sheet2...) ||-||-|| 成功 ")
        else:
            print(f" *** 输出数据表名称:Init 成功 ")

        print(f" *** 参数检查:Check 完成 ***")

        # 启动GUI应用
        app = QApplication(sys.argv)
        # 将参数传递给主窗口
        window = ExcelFilterSortApp(
            input_file_path, source_sheet_name, header_conditions,
            group_by_headers, sort_by_headers, output_file_path, output_sheet_name
        )
        window.show()
        # 执行应用循环，等待用户操作
        exit_code = app.exec_()

        # 根据窗口状态返回结果
        if window.export_successful:
            final_output_path = window.final_output_path
            print(f" >>> 当前已筛选出 {window.filtered_data.shape[0]} 行 <<< ")
            print(f" ***|||*** output ==> {final_output_path}")
            return final_output_path
        else:
            return None

    except Exception as e:
        print(f" *** 发生错误: {e} ***")
        return None


class DataLoaderThread(QThread):
    """
    在后台线程中加载Excel数据，避免阻塞GUI。
    """
    data_loaded = pyqtSignal(pd.DataFrame)  # 数据加载完成信号
    error_occurred = pyqtSignal(str)  # 发生错误信号

    def __init__(self, file_path, sheet_name):
        super().__init__()
        self.file_path = file_path
        self.sheet_name = sheet_name

    def run(self):
        try:
            # 使用openpyxl引擎加载指定工作表
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, engine='openpyxl')
            self.data_loaded.emit(df)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ExcelFilterSortApp(QMainWindow):
    """
    主窗口类，实现GUI逻辑。
    """

    def __init__(self, input_file, source_sheet, headers, group_headers, sort_headers, output_file, output_sheet):
        super().__init__()
        self.input_file = input_file
        self.source_sheet = source_sheet
        self.headers = headers
        self.group_headers = group_headers
        self.sort_headers = sort_headers
        self.output_file = output_file
        self.output_sheet = output_sheet

        # 内部状态
        self.df_original = None
        self.filtered_data = pd.DataFrame()
        self.final_output_path = None
        self.export_successful = False

        # GUI组件 - 初始化为空列表而不是None
        self.header_labels = []
        self.filter_line_edits = []
        self.table_widget = None
        self.row_count_label = None
        self.progress_bar = None
        self.data_loader_thread = None

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化用户界面。"""
        self.setWindowTitle('excel数据表筛选')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 修改后的 表头显示区和条件设置区 (两行对齐, 水平滚动) ---
        # 1. 创建一个QWidget作为容器
        header_widget = QWidget()
        # 2. 为这个容器设置QGridLayout
        header_grid_layout = QGridLayout(header_widget)
        header_grid_layout.setContentsMargins(0, 0, 0, 0)
        header_grid_layout.setHorizontalSpacing(5)  # 可调整列间距
        header_grid_layout.setVerticalSpacing(2)  # 可调整行间距

        # 3. 将这个容器放入QScrollArea
        header_scroll = QScrollArea()
        header_scroll.setWidgetResizable(True)
        header_scroll.setWidget(header_widget)
        header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 4. 设置一个合适的固定高度以容纳两行
        # header_scroll.setFixedHeight(80)
        required_height = 40 * 2 + header_grid_layout.verticalSpacing() + 20  # 估算值
        header_scroll.setFixedHeight(required_height)
        main_layout.addWidget(header_scroll)

        # --- 主要内容区 ---
        self.table_widget = QTableWidget()
        # 启用排序，但主要逻辑在自定义函数中
        # self.table_widget.setSortingEnabled(True)
        main_layout.addWidget(self.table_widget, 8)  # 占据大部分空间

        # --- 底部操作区 ---
        bottom_layout = QHBoxLayout()

        self.row_count_label = QLabel("当前数据行::0")
        bottom_layout.addWidget(self.row_count_label)

        # 添加一个弹簧，将按钮推到右侧
        bottom_layout.addStretch()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.apply_filters)
        bottom_layout.addWidget(refresh_btn)

        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_filters)
        bottom_layout.addWidget(reset_btn)

        confirm_btn = QPushButton("确定")
        confirm_btn.clicked.connect(self.export_data)
        bottom_layout.addWidget(confirm_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.close)
        bottom_layout.addWidget(cancel_btn)

        main_layout.addLayout(bottom_layout, 1)  # 占据小部分空间

        # --- 进度条 ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

    def load_data(self):
        """启动后台线程加载数据。"""
        self.progress_bar.setVisible(True)
        self.data_loader_thread = DataLoaderThread(self.input_file, self.source_sheet)
        self.data_loader_thread.data_loaded.connect(self.on_data_loaded)
        self.data_loader_thread.error_occurred.connect(self.on_load_error)
        self.data_loader_thread.start()

    def on_data_loaded(self, df):
        """数据加载完成后的回调。"""
        self.progress_bar.setVisible(False)
        self.df_original = df
        if self.df_original.empty:
            QMessageBox.warning(self, "警告", "加载的数据表为空。")
            return

        # 确定实际使用的表名和表头
        # source_sheet_name 为 None 或空时，pandas会加载第一个sheet
        sheet_name_used = self.source_sheet if self.source_sheet else self.df_original.columns.name or "Sheet1"

        # 确定用于筛选的表头
        all_headers_in_df = self.df_original.columns.tolist()
        if self.headers:
            # 严格匹配，区分大小写，去除首尾空格
            cleaned_input_headers = [h.strip() for h in self.headers]
            valid_headers = [h for h in cleaned_input_headers if h in all_headers_in_df]
            if not valid_headers:
                QMessageBox.warning(self, "警告", "指定的表头在数据表中均未找到。将使用所有表头。")
                valid_headers = all_headers_in_df
        else:
            valid_headers = all_headers_in_df

        print(f" *** {os.path.basename(self.input_file)}::{sheet_name_used} |-> {valid_headers}")

        # 更新DataFrame只保留有效列
        self.df_original = self.df_original[valid_headers]
        self.filtered_data = self.df_original.copy()

        # 初始化表头和输入框 (传入新的布局)
        # 注意：这里获取的是ScrollArea的widget，即我们创建的header_widget
        grid_layout = self.findChild(QScrollArea).widget().layout()
        self.setup_header_and_filter_area(valid_headers, grid_layout)
        # 显示所有原始数据
        self.display_data(self.df_original)

    def on_load_error(self, error_message):
        """数据加载出错的回调。"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", f"加载数据时出错: {error_message}")
        self.close()

    # 修改1: 改进setup_header_and_filter_area方法中的组件清理
    def setup_header_and_filter_area(self, headers, layout: QGridLayout):
        """动态设置表头显示区和条件设置区 (两行对齐)。"""
        # 更安全地清除旧的组件
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 清空列表
        self.header_labels.clear()
        self.filter_line_edits.clear()

        # 核心修改：使用GridLayout按行添加
        for i, header in enumerate(headers):
            # 表头标签 - 添加到第0行
            label = QLabel(header)
            label.setFixedWidth(150)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet("QLabel { border: 1px solid gray; background-color: #f0f0f0; padding: 2px;}")
            layout.addWidget(label, 0, i)
            self.header_labels.append(label)

            # 筛选输入框 - 添加到第1行，与标签同一列
            line_edit = QLineEdit()
            line_edit.setFixedWidth(150)
            line_edit.setPlaceholderText(f"筛选 {header}")
            line_edit.returnPressed.connect(self.apply_filters)
            # 使用lambda确保正确的参数传递，避免闭包问题
            line_edit.textChanged.connect(lambda text, le=line_edit: self.on_filter_text_changed())
            layout.addWidget(line_edit, 1, i)
            self.filter_line_edits.append(line_edit)

        # 添加一个可伸展的列
        layout.setColumnStretch(len(headers), 1)

    def on_filter_text_changed(self):
        """当任一筛选输入框文本改变时，启动定时器进行筛选，实现“实时”效果。"""
        # 确保定时器不会重复创建
        if not hasattr(self, '_filter_timer'):
            self._filter_timer = QTimer()
            self._filter_timer.setSingleShot(True)
            self._filter_timer.timeout.connect(self.apply_filters)

        # 重启定时器
        self._filter_timer.stop()
        self._filter_timer.start(300)  # 300ms延迟

    def apply_filters(self):
        """根据输入框条件应用筛选。"""
        if self.df_original is None or self.df_original.empty:
            return

        current_df = self.df_original.copy()
        filter_active = False

        for i, line_edit in enumerate(self.filter_line_edits):
            filter_text = line_edit.text().strip()  # 去除首尾空格
            header_name = self.header_labels[i].text()

            if filter_text:  # 如果输入框不为空，则应用筛选
                filter_active = True
                # 宽松匹配：筛选文本包含在单元格内容中
                # 处理NaN值，将其转换为字符串'nan'以便比较
                mask = current_df[header_name].astype(str).str.contains(filter_text, case=False, na=False)
                current_df = current_df[mask]

        if not filter_active:
            current_df = self.df_original.copy()

        self.filtered_data = current_df
        self.sort_and_display_data()

    def sort_and_display_data(self):
        """对筛选后的数据进行分组、排序，并显示。"""
        try:
            df_to_display = self.filtered_data.copy()

            # 如果需要分组
            if self.group_headers and all(h in df_to_display.columns for h in self.group_headers):
                try:
                    # 先按分组列排序，保证分组的稳定性
                    df_to_display = df_to_display.sort_values(by=self.group_headers)

                    # 创建分组
                    grouped = df_to_display.groupby(self.group_headers, sort=False, dropna=False)

                    # 准备排序后的数据列表
                    sorted_dfs = []

                    # 对每个分组进行组内排序
                    for name, group in grouped:
                        if self.sort_headers and all(h in group.columns for h in self.sort_headers):
                            try:
                                sorted_group = group.sort_values(by=self.sort_headers)
                            except Exception as sort_err:
                                print(f"组内排序时出错: {sort_err}")
                                sorted_group = group  # 排序失败则保持原样
                        else:
                            sorted_group = group
                        sorted_dfs.append(sorted_group)

                    # 如果有分组，重新组合数据
                    if sorted_dfs:
                        # 按照分组键的字典序对分组进行排序
                        try:
                            # 提取分组键并排序
                            group_keys = list(grouped.groups.keys())
                            # 如果group_keys是元组，需要特殊处理排序
                            if group_keys and isinstance(group_keys[0], tuple):
                                # 简单的字典序排序
                                sorted_keys = sorted(group_keys)
                            else:
                                sorted_keys = sorted(group_keys)

                            # 根据排序后的键重新排列分组
                            reordered_dfs = [grouped.get_group(key) for key in sorted_keys if key in grouped.groups]

                            # 对重新排序的分组再进行组内排序
                            final_sorted_dfs = []
                            for group_df in reordered_dfs:
                                if self.sort_headers and all(h in group_df.columns for h in self.sort_headers):
                                    try:
                                        sorted_group = group_df.sort_values(by=self.sort_headers)
                                    except Exception as sort_err:
                                        print(f"组内排序时出错: {sort_err}")
                                        sorted_group = group_df
                                else:
                                    sorted_group = group_df
                                final_sorted_dfs.append(sorted_group)

                            df_to_display = pd.concat(final_sorted_dfs, ignore_index=True)
                        except Exception as group_sort_err:
                            print(f"分组间排序时出错: {group_sort_err}")
                            # 如果分组间排序失败，就按原始分组顺序连接
                            df_to_display = pd.concat(sorted_dfs, ignore_index=True)
                    else:
                        df_to_display = pd.DataFrame()  # 如果没有分组成功，返回空

                except Exception as group_err:
                    print(f"分组时出错: {group_err}")
                    # 分组失败则跳过，直接显示筛选后的数据
            else:
                # 不分组，直接对整个筛选后的数据进行排序
                if self.sort_headers and all(h in df_to_display.columns for h in self.sort_headers):
                    try:
                        df_to_display = df_to_display.sort_values(by=self.sort_headers)
                    except Exception as sort_err:
                        print(f"整体排序时出错: {sort_err}")

            self.display_data(df_to_display)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"排序或显示数据时出错: {e}")
            self.display_data(self.filtered_data)  # 出错则显示未排序的筛选结果

    def display_data(self, df):
        """在表格中显示数据，并进行分组染色。"""
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)

        if df.empty:
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(1)
            item = QTableWidgetItem("无匹配数据")
            item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(0, 0, item)
            self.row_count_label.setText("当前数据行::0")
            return

        columns = df.columns.tolist()
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)

        # 设置列宽自适应内容
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        data = df.values.tolist()
        self.table_widget.setRowCount(len(data))

        # 分组染色逻辑
        color_map = {}
        current_color_index = 0
        colors = [QColor(255, 228, 196), QColor(230, 230, 250), QColor(240, 248, 255), QColor(245, 245, 220)]

        group_id_list = None
        if self.group_headers and all(h in df.columns for h in self.group_headers):
            try:
                group_id_list = df[self.group_headers].apply(lambda row: tuple(row), axis=1)
            except Exception:
                group_id_list = pd.Series([None] * len(df))

        for row_idx, row_data in enumerate(data):
            # 安全获取group_id
            group_id = None
            if group_id_list is not None and row_idx < len(group_id_list):
                group_id = group_id_list.iloc[row_idx]

            row_color = None
            if group_id is not None:
                if group_id not in color_map:
                    color_map[group_id] = colors[current_color_index % len(colors)]
                    current_color_index += 1
                row_color = color_map[group_id]

            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                if row_color:
                    item.setBackground(row_color)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table_widget.setItem(row_idx, col_idx, item)

        self.row_count_label.setText(f"当前数据行::{len(data)}")

    def reset_filters(self):
        """重置所有筛选条件。"""
        for line_edit in self.filter_line_edits:
            line_edit.clear()
        self.filtered_data = self.df_original.copy() if self.df_original is not None else pd.DataFrame()
        self.sort_and_display_data()

    # def export_data(self):
    #     """将当前筛选排序后的数据导出到Excel。"""
    #     if self.filtered_data.empty:
    #         QMessageBox.information(self, "信息", "没有数据需要导出。")
    #         return
    #
    #     try:
    #         output_path = self.output_file
    #         sheet_name = self.output_sheet
    #
    #         # 处理输出sheet名称
    #         final_sheet_name = sheet_name if sheet_name else "Sheet1"
    #
    #         # 检查文件是否存在
    #         if os.path.exists(output_path):
    #             with pd.ExcelFile(output_path, engine='openpyxl') as xls:
    #                 sheet_names = xls.sheet_names
    #                 if final_sheet_name in sheet_names:
    #                     # 如果Sheet名已存在，寻找下一个可用的Sheet名
    #                     counter = 1
    #                     while f"Sheet{counter}" in sheet_names:
    #                         counter += 1
    #                     final_sheet_name = f"Sheet{counter}"
    #         else:
    #             # 文件不存在，使用指定名称或默认名称
    #             if not sheet_name:
    #                 final_sheet_name = "Sheet1"
    #
    #         # 导出数据
    #         with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    #             self.filtered_data.to_excel(writer, sheet_name=final_sheet_name, index=False)
    #
    #         self.final_output_path = output_path
    #         self.export_successful = True
    #
    #         row_count = self.filtered_data.shape[0]
    #         print(
    #             f" *#* {os.path.basename(self.input_file)}::{self.source_sheet or self.df_original.columns.name or 'Sheet1'} ==> {row_count} 行.合法 -> {os.path.basename(output_path)}::{final_sheet_name}")
    #
    #         QMessageBox.information(self, "成功", f"数据已成功导出到:\n{output_path}\nSheet: {final_sheet_name}")
    #         self.close()
    #
    #     except Exception as e:
    #         QMessageBox.critical(self, "错误", f"导出数据时出错: {e}")

    def export_data(self):
        """将当前筛选排序后的数据导出到Excel。"""
        if self.filtered_data.empty:
            QMessageBox.information(self, "信息", "没有数据需要导出。")
            return

        try:
            output_path = self.output_file
            sheet_name = self.output_sheet

            # 处理输出sheet名称
            final_sheet_name = sheet_name if sheet_name else "Sheet1"

            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 检查文件是否存在
            if os.path.exists(output_path):
                # 文件存在，使用追加模式但可以覆盖指定sheet
                with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    self.filtered_data.to_excel(writer, sheet_name=final_sheet_name, index=False)
            else:
                # 文件不存在，使用写入模式
                with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
                    self.filtered_data.to_excel(writer, sheet_name=final_sheet_name, index=False)

            self.final_output_path = output_path
            self.export_successful = True

            row_count = self.filtered_data.shape[0]
            print(
                f" *#* {os.path.basename(self.input_file)}::{self.source_sheet or self.df_original.columns.name or 'Sheet1'} ==> {row_count} 行.合法 -> {os.path.basename(output_path)}::{final_sheet_name}")

            QMessageBox.information(self, "成功", f"数据已成功导出到:\n{output_path}\nSheet: {final_sheet_name}")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据时出错: {e}")

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        # 停止并清理定时器
        if hasattr(self, '_filter_timer'):
            self._filter_timer.stop()
            self._filter_timer.deleteLater()

        # 等待数据加载线程完成
        if self.data_loader_thread and self.data_loader_thread.isRunning():
            self.data_loader_thread.quit()
            self.data_loader_thread.wait()

        event.accept()


"""
基于PyQt5的Excel多条件筛选与分组排序GUI工具

该模块提供了一个函数 `GUI_XLSX_export_MultiCondition_MultiSort_RULE_0`，
用于在Windows系统下创建一个图形用户界面(GUI)，允许用户根据JSON规则（此处简化为直接输入）
对指定Excel文件中的数据进行多表头条件匹配筛选，并将结果分组排序后输出到另一个Excel文件。

依赖库:
- sys
- os
- json (虽然题目未明确使用，但可能用于未来扩展)
- pandas
- openpyxl
- PyQt5 (QtCore, QtGui, QtWidgets)

注意: 此代码旨在作为独立模块运行，包含完整的GUI逻辑。
     在实际项目中，日志记录部分应适配主程序的日志系统。
"""

# import sys
# import os
# # import json # 题目未涉及具体JSON解析，暂不导入
# import pandas as pd
# from openpyxl import Workbook, load_workbook
# from PyQt5.QtCore import Qt, QTimer, QAbstractTableModel, QModelIndex, pyqtSignal
# from PyQt5.QtGui import QColor, QFont
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#     QScrollArea, QLabel, QLineEdit, QPushButton, QTableView,
#     QMessageBox, QHeaderView, QSizePolicy
# )


# def GUI_XLSX_export_MultiCondition_MultiSort_RULE_0(
#         source_file_path: str,
#         source_sheet_name: str,
#         filter_headers: list,
#         group_by_headers: list,
#         sort_within_group_headers: list,
#         target_file_path: str,
#         target_sheet_name: str):
#     """
#     创建一个GUI，让用户可以对Excel文件进行多条件筛选、分组和排序，并导出结果。

#     :param source_file_path: 源Excel文件路径 (str, 必须)
#     :param source_sheet_name: 源数据表名称 (str, 可为空，默认第一个sheet)
#     :param filter_headers: 用于初步筛选的表头列表 (list, 可为空，默认全部)
#     :param group_by_headers: 分组依据的表头列表 (list, 可为空，默认不分组)
#     :param sort_within_group_headers: 组内排序依据的表头列表 (list, 可为空，默认组内不排序)
#     :param target_file_path: 目标Excel文件路径 (str, 必须)
#     :param target_sheet_name: 目标数据表名称 (str, 可为空，默认Sheet1, Sheet2,...)
#     :return: 成功时返回目标文件路径(str)，失败或取消时返回None
#     """

#     try:
#         print(f" *** 参数检查:Init 开始 ")

#         # --- 1. 初始化 + 检查 ---
#         if not source_file_path or not isinstance(source_file_path, str):
#             raise ValueError("源文件路径不能为空")
#         if not os.path.exists(source_file_path):
#             raise FileNotFoundError(f"源文件不存在: {source_file_path}")
#         print(f" *** 源文件路径检查:Check |-> {source_file_path} ||-||-|| 成功 ")

#         if not target_file_path or not isinstance(target_file_path, str):
#             raise ValueError("目标文件路径不能为空")
#         print(f" *** 目标文件路径检查:Check |-> {target_file_path} ||-||-|| 成功 ")
#         # 目标文件不存在则会在保存时自动创建

#         # 处理默认值
#         effective_source_sheet = source_sheet_name if source_sheet_name else None
#         effective_filter_headers = filter_headers if isinstance(filter_headers, list) and filter_headers else []
#         effective_group_by_headers = group_by_headers if isinstance(group_by_headers, list) and group_by_headers else []
#         effective_sort_within_group_headers = sort_within_group_headers if isinstance(sort_within_group_headers,
#                                                                                        list) and sort_within_group_headers else []
#         effective_target_sheet = target_sheet_name if target_sheet_name else None

#         default_applied_msg_parts = []
#         if not source_sheet_name: default_applied_msg_parts.append("源数据表名(默认首表)")
#         if not filter_headers: default_applied_msg_parts.append("筛选表头(默认全部)")
#         if not group_by_headers: default_applied_msg_parts.append("分组表头(默认无)")
#         if not sort_within_group_headers: default_applied_msg_parts.append("组内排序表头(默认无)")
#         if not target_sheet_name: default_applied_msg_parts.append("目标数据表名(默认SheetN)")

#         default_msg = " ||-||-|| ".join(default_applied_msg_parts) if default_applied_msg_parts else "无"
#         print(f" *** 默认参数应用:Init |-> {default_msg} ||-||-|| 成功 ")

#         result_data_list = []  # 存储最终筛选并排序后的结果
#         intermediate_groups_set = set() # 存储第一轮筛选出的分组标识元组集合

#         print(f" *** 初始化:Init 完成 ")

#         # --- 2. 读取源文件 ---
#         print(f" *** 数据加载:Init 开始 ")

#         # 使用openpyxl引擎提高效率，并只加载指定工作表
#         df_full = pd.read_excel(source_file_path, sheet_name=effective_source_sheet, engine='openpyxl')
#         actual_source_sheet_name = effective_source_sheet if effective_source_sheet else df_full.keys()[0]
#         df_source = df_full[actual_source_sheet_name] if isinstance(df_full, dict) else df_full

#         all_headers_in_source = df_source.columns.tolist()
#         print(f" *** 源数据表读取:Check |-> 表 '{actual_source_sheet_name}' 已读取 ||-||-|| 成功 ")

#         # 2.2 确定有效筛选表头
#         valid_filter_headers = []
#         if effective_filter_headers:
#             # 清除表头和筛选条件的首尾无效空格
#             cleaned_effective_filter_headers = [str(h).strip() for h in effective_filter_headers]
#             valid_filter_headers = [h for h in all_headers_in_source if str(h).strip() in cleaned_effective_filter_headers]
#         else:
#             valid_filter_headers = all_headers_in_source

#         print(f" *** {os.path.basename(source_file_path)}::{actual_source_sheet_name} |-> {valid_filter_headers}")

#         print(f" *** 数据加载:Init 完成 ")

#         # 启动GUI应用程序
#         app = QApplication(sys.argv)
#         main_window = ExcelFilterApp(
#             source_df=df_source.copy(),
#             valid_filter_headers=valid_filter_headers,
#             group_by_headers=effective_group_by_headers,
#             sort_within_group_headers=effective_sort_within_group_headers,
#             source_info=(os.path.basename(source_file_path), actual_source_sheet_name),
#             target_info=(target_file_path, effective_target_sheet),
#             result_callback=lambda data: setattr(sys.modules[__name__], '_temp_result_data', data) # 临时传递结果
#         )
#         main_window.show()
#         exit_code = app.exec_()

#         # 检查是否通过“确定”按钮正常退出
#         if exit_code == 0 and hasattr(sys.modules[__name__], '_temp_result_data'):
#             final_result_df = getattr(sys.modules[__name__], '_temp_result_data')
#             delattr(sys.modules[__name__], '_temp_result_data') # 清理临时变量

#             if final_result_df is not None and not final_result_df.empty:
#                 num_rows = len(final_result_df)

#                 # --- 3. 写入目标文件 ---
#                 # 确定有效的目标sheet名称
#                 effective_final_sheet_name = effective_target_sheet
#                 if not effective_final_sheet_name:
#                     if not os.path.exists(target_file_path):
#                         effective_final_sheet_name = "Sheet1"
#                     else:
#                         try:
#                             existing_wb = load_workbook(target_file_path)
#                             sheet_names = existing_wb.sheetnames
#                             i = 1
#                             while f"Sheet{i}" in sheet_names:
#                                 i += 1
#                             effective_final_sheet_name = f"Sheet{i}"
#                         except Exception as e:
#                             print(f"警告: 检查目标文件Sheet时出错 {e}, 将使用 'Sheet1'")
#                             effective_final_sheet_name = "Sheet1"

#                 # 写入Excel
#                 try:
#                     if not os.path.exists(target_file_path):
#                         wb = Workbook()
#                         if 'Sheet' in wb.sheetnames:
#                             std = wb['Sheet']
#                             wb.remove(std)
#                         ws = wb.create_sheet(title=effective_final_sheet_name)
#                         # pandas writer会处理header和data
#                         with pd.ExcelWriter(target_file_path, engine='openpyxl', mode='w', if_sheet_exists='replace') as writer:
#                             final_result_df.to_excel(writer, sheet_name=effective_final_sheet_name, index=False)
#                     else:
#                         with pd.ExcelWriter(target_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#                              final_result_df.to_excel(writer, sheet_name=effective_final_sheet_name, index=False)

#                     print(f" *#* {os.path.basename(source_file_path)}::{actual_source_sheet_name} ==> {num_rows} 行.合法 -> {os.path.basename(target_file_path)}::{effective_final_sheet_name}")
#                     print(f" >>> 当前已筛选出 {num_rows} 行 <<< \n ***|||*** output ==> {target_file_path}")
#                     return target_file_path
#                 except Exception as e:
#                     print(f"写入目标文件时发生错误: {e}")
#                     return None
#             else:
#                 print(" >>> 当前已筛选出 0 行 <<< \n ***|||*** 无数据导出")
#                 return target_file_path # 文件已创建或已存在，即使无数据也返回路径
#         else:
#             # 用户点击取消或关闭窗口
#             print("操作被用户取消。")
#             return None

#     except Exception as e:
#         print(f"函数执行过程中发生未预期的错误: {e}")
#         return None


# class PandasModel(QAbstractTableModel):
#     """用于在QTableView中显示Pandas DataFrame的模型"""
#     def __init__(self, df=pd.DataFrame(), group_info=None): # group_info: [(start_row, end_row, color), ...]
#         super().__init__()
#         self._df = df
#         self._group_info = group_info or []

#     def rowCount(self, parent=QModelIndex()):
#         return len(self._df.index)

#     def columnCount(self, parent=QModelIndex()):
#         return len(self._df.columns)

#     def data(self, index, role=Qt.DisplayRole):
#         if not index.isValid():
#             return None

#         row, col = index.row(), index.column()

#         if role == Qt.DisplayRole:
#             val = self._df.iat[row, col]
#             # 处理NaN等特殊值
#             if pd.isna(val):
#                 return ""
#             return str(val)

#         elif role == Qt.BackgroundRole:
#             for start_row, end_row, color in self._group_info:
#                 if start_row <= row < end_row:
#                     return color
#             return None

#         return None

#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Horizontal:
#                 return str(self._df.columns[section])
#             elif orientation == Qt.Vertical:
#                 return str(self._df.index[section] + 1) # 显示1-based行号
#         return None

#     def update_data(self, new_df, new_group_info=None):
#         self.beginResetModel()
#         self._df = new_df.reset_index(drop=True) # Ensure a clean integer index
#         self._group_info = new_group_info or []  # 修正：使用正确的参数名
#         self.endResetModel()


# class ExcelFilterApp(QMainWindow):
#     """主GUI应用程序窗口"""
#     def __init__(self, source_df, valid_filter_headers, group_by_headers, sort_within_group_headers, source_info, target_info, result_callback):
#         super().__init__()
#         self.source_df = source_df
#         self.all_headers = source_df.columns.tolist()
#         self.valid_filter_headers = valid_filter_headers
#         self.group_by_headers = group_by_headers
#         self.sort_within_group_headers = sort_within_group_headers
#         self.src_filename, self.src_sheetname = source_info
#         self.target_filepath, self.target_sheetname_template = target_info
#         self.result_callback = result_callback

#         self.current_filtered_df = self.source_df.copy()
#         self.final_sorted_df = pd.DataFrame()
#         self.group_color_mapping = {}
#         self.group_display_info = [] # [(start_row, end_row, color), ...]
#         self.intermediate_groups_set = set()

#         self.filter_line_edits = {}
#         self.init_ui()
#         self.update_main_table(self.current_filtered_df) # 初始显示所有数据

#     def init_ui(self):
#         self.setWindowTitle('excel数据表筛选')
#         self.setGeometry(100, 100, 1200, 800)

#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         main_layout = QVBoxLayout(central_widget)

#         # --- 表头显示区 和 条件设置区 (放在一个可滚动的水平区域) ---
#         header_and_filter_area = QWidget()
#         header_and_filter_layout = QHBoxLayout(header_and_filter_area)
#         header_and_filter_layout.setContentsMargins(0, 0, 0, 0)

#         header_scroll = QScrollArea()
#         header_scroll.setWidgetResizable(True)
#         header_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#         header_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         header_container = QWidget()
#         header_layout = QHBoxLayout(header_container)
#         header_layout.setSpacing(5)
#         header_layout.setAlignment(Qt.AlignLeft)

#         filter_scroll = QScrollArea()
#         filter_scroll.setWidgetResizable(True)
#         filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#         filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         filter_container = QWidget()
#         filter_layout = QHBoxLayout(filter_container)
#         filter_layout.setSpacing(5)
#         filter_layout.setAlignment(Qt.AlignLeft)

#         for header in self.all_headers:
#             # 表头标签
#             header_label = QLabel(str(header))
#             header_label.setStyleSheet("font-weight: bold; border: 1px solid gray; padding: 2px;")
#             header_label.setMinimumWidth(100) # 设置最小宽度以便对齐
#             header_layout.addWidget(header_label)

#             # 对应的筛选输入框 (仅对有效筛选表头)
#             line_edit = QLineEdit()
#             line_edit.setMinimumWidth(100)
#             line_edit.setObjectName(f"filter_{header}") # 便于查找
#             if header in self.valid_filter_headers:
#                 line_edit.returnPressed.connect(lambda h=header: self.apply_filters()) # lambda捕获当前header
#                 self.filter_line_edits[header] = line_edit
#             else:
#                 line_edit.setPlaceholderText("非筛选项")
#                 line_edit.setEnabled(False)
#             filter_layout.addWidget(line_edit)

#         header_scroll.setWidget(header_container)
#         filter_scroll.setWidget(filter_container)
#         header_and_filter_layout.addWidget(header_scroll)
#         header_and_filter_layout.addWidget(filter_scroll)

#         main_layout.addWidget(header_and_filter_area)

#         # --- 主要内容区 (表格视图) ---
#         self.table_view = QTableView()
#         self.table_model = PandasModel(pd.DataFrame())
#         self.table_view.setModel(self.table_model)
#         self.table_view.setAlternatingRowColors(True)
#         self.table_view.horizontalHeader().setStretchLastSection(True)
#         self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
#         self.table_view.verticalHeader().setDefaultSectionSize(20) # 调整行高
#         main_layout.addWidget(self.table_view, 8) # 占据大部分空间

#         # --- 底部操作区 ---
#         bottom_panel = QWidget()
#         bottom_layout = QHBoxLayout(bottom_panel)

#         self.count_label = QLabel("当前数据行::0")
#         bottom_layout.addWidget(self.count_label)

#         bottom_spacer = QWidget()
#         bottom_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
#         bottom_layout.addWidget(bottom_spacer)

#         self.refresh_button = QPushButton("刷新")
#         self.reset_button = QPushButton("重置")
#         self.confirm_button = QPushButton("确定")
#         self.cancel_button = QPushButton("取消")

#         self.refresh_button.clicked.connect(self.apply_filters)
#         self.reset_button.clicked.connect(self.reset_filters)
#         self.confirm_button.clicked.connect(self.on_confirm)
#         self.cancel_button.clicked.connect(self.close)

#         button_layout = QHBoxLayout()
#         button_layout.addWidget(self.refresh_button)
#         button_layout.addWidget(self.reset_button)
#         button_layout.addWidget(self.confirm_button)
#         button_layout.addWidget(self.cancel_button)
#         bottom_layout.addLayout(button_layout)

#         main_layout.addWidget(bottom_panel, 1)

#     def apply_filters(self):
#         """根据输入框内容进行筛选"""
#         conditions = {}
#         for header, le in self.filter_line_edits.items():
#             text = le.text().strip() # 清除首尾空格
#             if text:
#                 conditions[header] = text

#         if not conditions:
#             self.current_filtered_df = self.source_df.copy()
#         else:
#             mask = pd.Series([True] * len(self.source_df), index=self.source_df.index)
#             for col, pattern in conditions.items():
#                 # 宽松匹配：只要单元格内容包含pattern即可
#                 col_mask = self.source_df[col].astype(str).str.contains(pattern, case=False, na=False)
#                 mask &= col_mask
#             self.current_filtered_df = self.source_df[mask].copy()

#         # 执行第一轮筛选：生成分组标识
#         self.intermediate_groups_set.clear()
#         if self.group_by_headers and not self.current_filtered_df.empty:
#              # 提取用于分组的列，并去重
#              if all(col in self.current_filtered_df.columns for col in self.group_by_headers):
#                  group_cols_data = self.current_filtered_df[self.group_by_headers]
#                  for _, row in group_cols_data.iterrows():
#                      group_key_tuple = tuple(row)
#                      if group_key_tuple not in self.intermediate_groups_set:
#                          self.intermediate_groups_set.add(group_key_tuple)
#                          # print(f" *** {self.src_filename}::{self.src_sheetname}.row == N/A ||-> T ==> (ADD)_({', '.join(map(str, group_key_tuple))})")
#                      # else: # 可选打印重复
#                      #     print(f" *** {self.src_filename}::{self.src_sheetname}.row == N/A ||-> T ==> (Repeat)_({', '.join(map(str, group_key_tuple))})")


#         self.perform_second_round_filter_and_sort()

#     def perform_second_round_filter_and_sort(self):
#         """执行第二轮筛选、分组、排序"""
#         if self.current_filtered_df.empty:
#             self.final_sorted_df = pd.DataFrame()
#             self.group_display_info = []
#             self.update_count_label(0)
#             self.update_main_table(self.final_sorted_df)
#             return

#         if not self.group_by_headers:
#             # 不分组，直接按组内排序规则排
#             self.final_sorted_df = self.current_filtered_df.copy()
#             if self.sort_within_group_headers:
#                 # 检查排序列是否存在
#                 sort_cols_exist = [col for col in self.sort_within_group_headers if col in self.final_sorted_df.columns]
#                 if sort_cols_exist:
#                      self.final_sorted_df.sort_values(by=sort_cols_exist, inplace=True)
#             self.group_display_info = []
#         else:
#             # 需要分组
#             # 检查分组列是否存在
#             group_cols_exist = [col for col in self.group_by_headers if col in self.current_filtered_df.columns]
#             if not group_cols_exist:
#                  self.final_sorted_df = self.current_filtered_df.copy()
#                  self.group_display_info = []
#             else:
#                 # 第二轮筛选：基于第一轮得到的分组标识
#                 if not self.intermediate_groups_set:
#                     self.final_sorted_df = pd.DataFrame()
#                     self.group_display_info = []
#                 else:
#                     mask_second_round = pd.Series([False] * len(self.current_filtered_df), index=self.current_filtered_df.index)
#                     for idx, row in self.current_filtered_df.iterrows():
#                         group_key = tuple(row[group_cols_exist])
#                         if group_key in self.intermediate_groups_set:
#                             mask_second_round.loc[idx] = True
#                     filtered_for_grouping_df = self.current_filtered_df[mask_second_round].copy()

#                     if filtered_for_grouping_df.empty:
#                         self.final_sorted_df = pd.DataFrame()
#                         self.group_display_info = []
#                     else:
#                         # --- 分组 ---
#                         grouped = filtered_for_grouping_df.groupby(group_cols_exist, sort=False)

#                         # --- 组间排序 ---
#                         sorted_groups_keys = list(grouped.groups.keys())
#                         if sorted_groups_keys and isinstance(sorted_groups_keys[0], tuple):
#                             # 多列排序
#                             sorted_groups_keys.sort(key=lambda x: tuple(str(v) for v in x))
#                         else:
#                             sorted_groups_keys.sort(key=lambda x: str(x))

#                         # --- 分组染色和组装 ---
#                         self.group_display_info = []
#                         ordered_dfs = []
#                         color_idx = 0
#                         colors = [QColor(255, 220, 220), QColor(220, 255, 220), QColor(220, 220, 255),
#                                   QColor(255, 255, 220), QColor(255, 220, 255), QColor(220, 255, 255)]

#                         current_row_offset = 0
#                         for group_key in sorted_groups_keys:
#                             group_df = grouped.get_group(group_key).copy()

#                             # --- 组内排序 ---
#                             if self.sort_within_group_headers:
#                                 sort_cols_exist_inner = [col for col in self.sort_within_group_headers if col in group_df.columns]
#                                 if sort_cols_exist_inner:
#                                     group_df.sort_values(by=sort_cols_exist_inner, inplace=True)

#                             ordered_dfs.append(group_df)

#                             group_size = len(group_df)
#                             color = colors[color_idx % len(colors)]
#                             self.group_display_info.append((current_row_offset, current_row_offset + group_size, color))
#                             current_row_offset += group_size
#                             color_idx += 1

#                         self.final_sorted_df = pd.concat(ordered_dfs, ignore_index=True) if ordered_dfs else pd.DataFrame()

#         self.update_count_label(len(self.final_sorted_df))
#         self.update_main_table(self.final_sorted_df)


#     def reset_filters(self):
#         """重置所有筛选条件"""
#         for le in self.filter_line_edits.values():
#             le.clear()
#         self.current_filtered_df = self.source_df.copy()
#         # 重置后也需要重新执行二轮筛选和排序以更新显示
#         self.intermediate_groups_set.clear()
#         self.perform_second_round_filter_and_sort()

#     def update_main_table(self, df_to_show: pd.DataFrame):
#         """更新主表格视图"""
#         self.table_model.update_data(df_to_show, self.group_display_info)
#         QTimer.singleShot(0, lambda: self.table_view.resizeColumnsToContents()) # 异步调整列宽

#     def update_count_label(self, count: int):
#         """更新底部计数标签"""
#         self.count_label.setText(f"当前数据行::{count}")

#     def on_confirm(self):
#         """处理“确定”按钮点击事件"""
#         # 将最终结果传递回调用者
#         self.result_callback(self.final_sorted_df)
#         # 正常退出
#         QApplication.instance().exit(0)

#     def closeEvent(self, event):
#         """处理窗口关闭事件"""
#         # 如果不是通过“确定”按钮关闭，则认为是取消
#         if QApplication.instance().closingDown(): # 这种检查不太可靠，但我们用exit code来区分
#              pass # 由exec_的返回值判断
#         event.accept()


import sys
import os
import pandas as pd
from PyQt5.QtCore import Qt, QTimer, QAbstractTableModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableView, QHeaderView,
    QMessageBox, QScrollArea, QFrame
)


def GUI_XLSX_export_MultiCondition_MultiSort_RULE_0(
        source_file_path,
        source_sheet_name,
        filter_headers_list,
        group_by_headers_list,
        sort_within_group_headers_list,
        target_file_path,
        target_sheet_name):
    """
    实现一个本地图形化界面，用于对指定Excel文件的数据表进行多表头条件匹配筛选，
    并将符合条件的数据输出到指定Excel文件中，同时支持分组和排序。

    :param source_file_path: str, 源Excel文件路径（相对或绝对），不能为空。
    :param source_sheet_name: str, 源数据表名称，为空则使用第一个表。
    :param filter_headers_list: list, 用于筛选的表头列表，为空则使用所有表头。
    :param group_by_headers_list: list, 分组依据的表头列表，为空则不分组。
    :param sort_within_group_headers_list: list, 组内排序依据的表头列表，为空则不排序。
    :param target_file_path: str, 目标Excel文件路径（相对或绝对），不能为空。
    :param target_sheet_name: str, 目标数据表名称，为空则自动命名。
    :return: str or None, 成功时返回目标文件路径，失败或取消时返回None。
    """

    # --- 1. 初始化+检查 ---
    print(f" *** 参数检查与初始化: 开始 ...")

    if not source_file_path or not os.path.exists(source_file_path):
        error_msg = f"源文件路径 '{source_file_path}' 无效或不存在。"
        print(error_msg)
        return None
    print(" *** 源文件路径检查: 成功")

    if not target_file_path:
        error_msg = "目标文件路径不能为空。"
        print(error_msg)
        return None
    # 目标文件不存在则会在保存时自动创建
    print(" *** 目标文件路径检查: 成功")

    app = QApplication.instance()  # 检查是否已有实例
    if app is None:
        app = QApplication(sys.argv)

    try:
        window = ExcelFilterWindow(
            source_file_path,
            source_sheet_name,
            filter_headers_list,
            group_by_headers_list,
            sort_within_group_headers_list,
            target_file_path,
            target_sheet_name
        )
        window.show()
        exit_code = app.exec_()

        if exit_code == 0 and hasattr(window, 'final_result_df') and window.final_result_df is not None:
            # 导出最终结果DataFrame到Excel
            result_df = window.final_result_df
            final_target_sheet = window.determine_final_sheet_name(target_file_path, target_sheet_name)

            with pd.ExcelWriter(target_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                result_df.to_excel(writer, sheet_name=final_target_sheet, index=False)

            print(
                f" *#* {os.path.basename(source_file_path)}::{window.actual_source_sheet} ==> {len(result_df)} 行.合法 -> {os.path.basename(target_file_path)}::{final_target_sheet}")
            print(f" >>> 当前已筛选出 {len(result_df)} 行 <<< \n ***|||*** output ==> {target_file_path}")
            return target_file_path
        else:
            print("操作被取消或未完成。")
            return None

    except Exception as e:
        print(f"发生未预期的错误: {e}")
        return None


class PandasModel(QAbstractTableModel):
    """自定义模型，用于在QTableView中高效显示pandas DataFrame."""

    def __init__(self, df=pd.DataFrame(), colors=None):
        super().__init__()
        self._df = df.copy()  # 创建副本以防意外修改原数据
        self.colors = colors if colors is not None else {}

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns) if not self._df.empty else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            val = self._df.iat[row, col]
            # 处理NaN值
            if pd.isna(val):
                return ""
            return str(val)

        elif role == Qt.BackgroundRole:
            color_info = self.colors.get(row)
            if color_info:
                return QColor(color_info['color'])

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self._df.columns):
                    return str(self._df.columns[section])
            elif orientation == Qt.Vertical:
                return str(section + 1)  # 显示行号从1开始
        return None

    def update_data(self, new_df, new_colors=None):
        self.beginResetModel()
        self._df = new_df.copy()
        self.colors = new_colors if new_colors is not None else {}
        self.endResetModel()


class ExcelFilterWindow(QMainWindow):
    def __init__(self, source_file_path, source_sheet_name, filter_headers_list,
                 group_by_headers_list, sort_within_group_headers_list,
                 target_file_path, target_sheet_name):
        super().__init__()

        self.source_file_path = source_file_path
        self.requested_source_sheet = source_file_path
        self.filter_headers_list = filter_headers_list or []
        self.group_by_headers_list = group_by_headers_list or []
        self.sort_within_group_headers_list = sort_within_group_headers_list or []
        self.target_file_path = target_file_path
        self.requested_target_sheet = target_sheet_name

        self.setWindowTitle("excel数据表筛选")
        self.resize(1200, 800)

        # 存储原始数据、过滤后数据和最终结果
        self.original_df = None
        self.filtered_dfs = {}  # 缓存中间筛选结果
        self.final_result_df = None

        # UI组件
        self.header_labels = []
        self.filter_line_edits = []
        self.table_view = None
        self.status_label = None
        self.model = None

        # 加载数据并构建UI
        self.load_initial_data()
        self.init_ui()
        self.update_display()  # 初始显示所有数据

    def load_initial_data(self):
        """加载初始Excel数据"""
        try:
            print(" *** 数据加载: 开始 ...")
            excel_file = pd.ExcelFile(self.source_file_path, engine='openpyxl')
            sheets = excel_file.sheet_names
            print(f" *** 工作簿中的工作表: {sheets}")

            # 确定要读取的工作表
            if self.requested_source_sheet and self.requested_source_sheet in sheets:
                self.actual_source_sheet = self.requested_source_sheet
            else:
                self.actual_source_sheet = sheets[0] if sheets else None

            if not self.actual_source_sheet:
                raise ValueError("无法确定源数据表。")

            print(f" *** 要读取的数据表: {self.actual_source_sheet} ||-||-|| 成功 ")

            # 读取特定工作表
            self.original_df = pd.read_excel(self.source_file_path, sheet_name=self.actual_source_sheet,
                                             engine='openpyxl')
            print(" *** 原始数据加载: 完成 ")

            # 确定可用的列头
            all_headers = list(self.original_df.columns)
            print(f" *** 源数据表所有表头: {all_headers}")

            # 处理filter_headers_list：去除首尾空格并严格匹配
            cleaned_filter_headers = [h.strip() for h in self.filter_headers_list]

            if not cleaned_filter_headers:
                self.valid_filter_headers = all_headers
                print(f" *** 解析筛选表头: 使用所有表头 ||-||-|| 成功 ")
            else:
                self.valid_filter_headers = [h for h in cleaned_filter_headers if h in all_headers]
                unmatched = set(cleaned_filter_headers) - set(all_headers)
                if unmatched:
                    print(f" *** 警告: 请求的筛选表头未在数据表中找到: {unmatched}")
                print(f" *** 解析筛选表头: {self.valid_filter_headers} ||-||-|| 成功 ")

        except Exception as e:
            print(f"加载数据时出错: {e}")
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")
            self.close()

    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 表头显示区 & 条件设置区 (带水平滚动) ---
        header_condition_area = QScrollArea()
        header_condition_area.setWidgetResizable(True)
        header_condition_container = QWidget()
        header_condition_layout = QVBoxLayout(header_condition_container)
        header_condition_layout.setContentsMargins(0, 0, 0, 0)
        header_condition_layout.setSpacing(0)

        # 表头标签行
        headers_layout = QHBoxLayout()
        headers_layout.addStretch(1)  # 添加弹性空间
        headers_layout.setSpacing(10)
        for header in self.valid_filter_headers:
            label = QLabel(header)
            label.setStyleSheet("border: 1px solid gray; padding: 5px;")
            label.setMinimumWidth(150)  # 设置最小宽度使对齐更明显
            headers_layout.addWidget(label)
            self.header_labels.append(label)
        headers_layout.addStretch(1)  # 添加弹性空间
        header_row_widget = QWidget()
        header_row_widget.setLayout(headers_layout)
        header_condition_layout.addWidget(header_row_widget)

        # 条件输入框行
        filters_layout = QHBoxLayout()
        filters_layout.addStretch(1)  # 添加弹性空间
        filters_layout.setSpacing(10)
        for i, header in enumerate(self.valid_filter_headers):
            line_edit = QLineEdit()
            line_edit.setObjectName(f"filter_{i}")  # 方便查找
            line_edit.setMinimumWidth(150)
            line_edit.returnPressed.connect(self.on_filter_changed)  # 回车触发筛选
            # 可选：连接textChanged信号实现实时筛选 (可能性能开销较大)
            # line_edit.textChanged.connect(lambda text, idx=i: self.on_real_time_filter_change(idx, text))
            filters_layout.addWidget(line_edit)
            self.filter_line_edits.append(line_edit)
        filters_layout.addStretch(1)  # 添加弹性空间
        filter_row_widget = QWidget()
        filter_row_widget.setLayout(filters_layout)
        header_condition_layout.addWidget(filter_row_widget)

        header_condition_area.setWidget(header_condition_container)
        main_layout.addWidget(header_condition_area)

        # --- 主要内容区 (表格视图) ---
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.verticalHeader().setVisible(True)
        self.model = PandasModel(pd.DataFrame())  # 初始化空模型
        self.table_view.setModel(self.model)
        main_layout.addWidget(self.table_view, stretch=4)  # 占据大部分空间

        # --- 底部操作区 ---
        bottom_layout = QHBoxLayout()

        self.status_label = QLabel("当前数据行::0")
        bottom_layout.addWidget(self.status_label)

        bottom_layout.addStretch(1)  # 推动按钮到右侧

        refresh_btn = QPushButton("刷新")
        reset_btn = QPushButton("重置")
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")

        refresh_btn.clicked.connect(self.on_refresh_clicked)
        reset_btn.clicked.connect(self.on_reset_clicked)
        ok_btn.clicked.connect(self.on_ok_clicked)
        cancel_btn.clicked.connect(self.on_cancel_clicked)

        button_width = 80
        refresh_btn.setFixedWidth(button_width)
        reset_btn.setFixedWidth(button_width)
        ok_btn.setFixedWidth(button_width)
        cancel_btn.setFixedWidth(button_width)

        bottom_layout.addWidget(refresh_btn)
        bottom_layout.addWidget(reset_btn)
        bottom_layout.addWidget(ok_btn)
        bottom_layout.addWidget(cancel_btn)

        main_layout.addLayout(bottom_layout)

    def get_current_filters(self):
        """获取当前所有非空的筛选条件"""
        filters = {}
        for i, le in enumerate(self.filter_line_edits):
            text = le.text().strip()  # 获取并清理文本
            if text:
                header = self.valid_filter_headers[i]
                filters[header] = text
        return filters

    def on_filter_changed(self):
        """当用户按下回车键时触发筛选"""
        self.apply_filters_and_update_display()

    # def on_real_time_filter_change(self, index, text):
    #     """实时筛选变更槽函数 (可选启用)"""
    #     # 注意：频繁调用可能导致界面卡顿，特别是大数据集
    #     # 可考虑使用 QTimer.singleShot 实现防抖
    #     QTimer.singleShot(300, self.apply_filters_and_update_display)

    def apply_filters_and_update_display(self):
        """应用筛选器并对结果进行分组排序后更新显示"""
        current_filters = self.get_current_filters()
        cache_key = tuple(sorted(current_filters.items()))

        # 尝试从缓存获取筛选结果
        if cache_key in self.filtered_dfs:
            filtered_df = self.filtered_dfs[cache_key].copy()
            print(" *** 筛选: 使用缓存结果 ...")
        else:
            print(" *** 筛选: 计算新结果 ...")
            if not current_filters:
                filtered_df = self.original_df.copy()
            else:
                mask = pd.Series([True] * len(self.original_df), dtype=bool)
                for header, condition_text in current_filters.items():
                    if header in self.original_df.columns:
                        # 宽松匹配：包含即可
                        series_to_check = self.original_df[header].astype(str).str.strip()
                        condition_mask = series_to_check.str.contains(condition_text, case=False, na=False)
                        old_mask_count = mask.sum()
                        mask &= condition_mask

                        # 日志打印每行筛选结果
                        for idx, row in self.original_df.iterrows():
                            row_num = idx + 1
                            cell_value_str = str(row[header]).strip()
                            is_match = condition_text.lower() in cell_value_str.lower()
                            match_status = "T" if is_match else "F"

                            # 构造分组元组用于日志
                            group_values = tuple(
                                str(row[group_col]).strip() for group_col in self.group_by_headers_list if
                                group_col in self.original_df.columns)
                            add_or_repeat = "Repeat" if group_values in [tuple(
                                str(r[g]).strip() for g in self.group_by_headers_list if g in self.original_df.columns)
                                                                         for _, r in
                                                                         self.original_df[mask].iterrows()] else "ADD"
                            print(
                                f" *** {os.path.basename(self.source_file_path)}::{self.actual_source_sheet}.row == {row_num} ||-> {match_status} ==> ({add_or_repeat})_{group_values}")

                filtered_df = self.original_df[mask].copy()

            # 缓存结果
            self.filtered_dfs[cache_key] = filtered_df.copy()

        # 第二轮筛选及后续处理
        if not filtered_df.empty and self.group_by_headers_list:
            # 提取分组字段并去重
            if any(col not in filtered_df.columns for col in self.group_by_headers_list):
                missing_cols = [col for col in self.group_by_headers_list if col not in filtered_df.columns]
                print(f"警告: 分组所需列缺失: {missing_cols}")
                grouped_keys_df = pd.DataFrame(columns=self.group_by_headers_list)
            else:
                grouped_keys_df = filtered_df[self.group_by_headers_list].drop_duplicates().reset_index(drop=True)

            # 构建第二轮筛选掩码
            second_round_mask = pd.Series([False] * len(self.original_df), dtype=bool)
            for _, group_row in grouped_keys_df.iterrows():
                group_mask = pd.Series([True] * len(self.original_df), dtype=bool)
                for col in self.group_by_headers_list:
                    group_mask &= (self.original_df[col].astype(str).str.strip() == str(group_row[col]).strip())
                second_round_mask |= group_mask

            final_filtered_df = self.original_df[second_round_mask].copy()

        else:
            final_filtered_df = filtered_df.copy()

        # 分组和排序
        sorted_df_with_colors = self.sort_and_colorize(final_filtered_df)

        # 更新模型和视图
        self.model.update_data(sorted_df_with_colors['data'], sorted_df_with_colors['colors'])
        self.final_result_df = sorted_df_with_colors['data']  # 保存最终结果供导出
        self.status_label.setText(f"当前数据行::{len(sorted_df_with_colors['data'])}")

    def sort_and_colorize(self, df):
        """对DataFrame进行分组、着色和排序"""
        if df.empty:
            return {'data': df, 'colors': {}}

        working_df = df.copy()

        # 如果没有分组要求，则直接进行全局排序（如果需要）
        if not self.group_by_headers_list:
            print(" *** 排序: 跳过分组阶段 ...")
            cols_for_global_sort = [c for c in self.sort_within_group_headers_list if c in working_df.columns]
            if cols_for_global_sort:
                print(f" *** 全局排序: 按 {cols_for_global_sort} ...")
                working_df.sort_values(by=cols_for_global_sort, inplace=True)
            return {'data': working_df.reset_index(drop=True), 'colors': {}}

        # 检查分组列是否存在
        missing_group_cols = [col for col in self.group_by_headers_list if col not in working_df.columns]
        if missing_group_cols:
            print(f" *** 错误: 分组列 {missing_group_cols} 在数据中不存在。跳过分组。")
            return {'data': working_df, 'colors': {}}

        # 1. 分组
        print(f" *** 分组: 按 {self.group_by_headers_list} ...")
        grouped = working_df.groupby(self.group_by_headers_list, sort=False)  # sort=False保留首次出现顺序作为组间初始顺序

        # 2. 组间排序
        valid_group_sort_cols = [c for c in self.group_by_headers_list if c in working_df.columns]
        if valid_group_sort_cols:
            print(f" *** 组间排序: 按 {valid_group_sort_cols} ...")
            # 我们通过对分组键进行排序来实现组间排序
            sorted_groups_keys = sorted(grouped.groups.keys(), key=lambda x: [
                x[list(self.group_by_headers_list).index(c)] if isinstance(x, tuple) else x for c in
                valid_group_sort_cols])
        else:
            sorted_groups_keys = list(grouped.groups.keys())

        # 3. 组内排序和合并
        merged_rows = []
        row_colors = {}
        predefined_colors = [
            QColor(255, 228, 225),  # MistyRose
            QColor(240, 248, 255),  # AliceBlue
            QColor(245, 245, 220),  # Beige
            QColor(240, 255, 240),  # Honeydew
            QColor(255, 250, 205),  # LemonChiffon
            QColor(255, 240, 245),  # LavenderBlush
            QColor(240, 255, 255),  # Azure
            QColor(255, 255, 240),  # Ivory
        ]

        color_idx = 0
        global_row_counter = 0
        for group_key in sorted_groups_keys:
            group_df = grouped.get_group(group_key).copy()

            # 组内排序
            valid_intra_sort_cols = [c for c in self.sort_within_group_headers_list if c in group_df.columns]
            if valid_intra_sort_cols:
                print(f" *** 组 '{group_key}' 内排序: 按 {valid_intra_sort_cols} ...")
                group_df.sort_values(by=valid_intra_sort_cols, inplace=True)

            group_start_row = global_row_counter
            for _, row in group_df.iterrows():
                merged_rows.append(row)
                # 为整行分配颜色信息
                row_colors[global_row_counter] = {'color': predefined_colors[color_idx % len(predefined_colors)],
                                                  'group': group_key}
                global_row_counter += 1

            color_idx += 1  # 下一组换颜色

        if not merged_rows:  # 防止空列表导致错误
            final_sorted_df = pd.DataFrame(columns=working_df.columns)
        else:
            final_sorted_df = pd.DataFrame(merged_rows).reset_index(drop=True)

        return {'data': final_sorted_df, 'colors': row_colors}

    def update_display(self):
        """更新主表格显示（初始加载所有数据）"""
        if self.original_df is not None:
            sorted_all_data = self.sort_and_colorize(self.original_df)
            self.model.update_data(sorted_all_data['data'], sorted_all_data['colors'])
            self.status_label.setText(f"当前数据行::{len(sorted_all_data['data'])}")

    def determine_final_sheet_name(self, file_path, requested_name):
        """确定最终写入的sheet name"""
        if requested_name:
            return requested_name

        existing_sheets = []
        if os.path.exists(file_path):
            try:
                with pd.ExcelFile(file_path, engine='openpyxl') as xls:
                    existing_sheets = xls.sheet_names
            except Exception as e:
                print(f"读取现有目标文件Sheet名时出错: {e}")
                existing_sheets = []

        base_name = "Sheet"
        counter = 1
        while True:
            candidate_name = f"{base_name}{counter}"
            if candidate_name not in existing_sheets:
                return candidate_name
            counter += 1

    def on_refresh_clicked(self):
        """刷新按钮点击事件"""
        print(" *** 用户操作: 刷新 ...")
        self.apply_filters_and_update_display()

    def on_reset_clicked(self):
        """重置按钮点击事件"""
        print(" *** 用户操作: 重置 ...")
        for le in self.filter_line_edits:
            le.clear()
        self.filtered_dfs.clear()  # 清除缓存
        self.update_display()  # 重新显示所有数据

    def on_ok_clicked(self):
        """确定按钮点击事件"""
        print(" *** 用户操作: 确认 ...")
        # 最终结果已在 self.final_result_df 中
        self.accept()

    def on_cancel_clicked(self):
        """取消按钮点击事件"""
        print(" *** 用户操作: 取消 ...")
        self.reject()

    def accept(self):
        """模拟 QDialog 的 accept 方法"""
        self.close()

    def reject(self):
        """模拟 QDialog 的 reject 方法"""
        self.final_result_df = None  # 标记为取消
        self.close()


# --- 示例用法 ---
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # result_path = GUI_XLSX_export_MultiCondition(
    #     src_file_path=r"temp\merged_output.xlsx",
    #     src_sheet_names=[],
    #     header_conditions=[],
    #     dst_file_path=r"./test.xlsx",
    #     dst_sheet_name=""
    #     )
    # if result_path:
    #     print(f"筛选完成，结果已保存至: {result_path}")
    # else:
    #     print("操作被取消或发生错误。")

    # 示例参数
    # input_path = r"temp\merged_output.xlsx"
    # source_sheet = r"Sheet1" # 或者 None
    # headers = [] # 或者 None
    # group_headers = [ "凭证编号", "凭证日期"] # 或者 []
    # sort_headers = [ "会计期间", "科目编号", "一级科目编号"] # 或者 []
    # output_path = r"test.xlsx"
    # output_sheet = None # 或者 None

    # result_path = GUI_XLSX_export_MultiCondition_MultiSort(
    #     input_path, source_sheet, headers,
    #     group_headers, sort_headers,
    #     output_path, output_sheet
    # )
    # if result_path:
    #     print(f"操作成功，文件已保存至: {result_path}")
    # else:
    #     print("操作被取消或失败。")

    # 示例参数 (请根据实际情况修改路径和文件名)
    source_fp = r"temp\merged_output.xlsx"  # 替换为你的源文件路径
    source_sn = ""  # 留空则使用第一个sheet
    filter_hl = []  # 留空则使用所有表头
    group_hl = ["凭证编号", "凭证日期"]  # 根据你的数据调整
    sort_hl = ["会计期间"]  # 根据你的数据调整
    target_fp = "筛选结果导出.xlsx"  # 替换为你的目标文件路径
    target_sn = ""  # 留空则自动命名Sheet

    result_path = GUI_XLSX_export_MultiCondition_MultiSort_RULE_0(
        source_fp, source_sn, filter_hl, group_hl, sort_hl, target_fp, target_sn
    )

    if result_path:
        print(f"成功导出到: {result_path}")
    else:
        print("操作未完成或已取消。")
