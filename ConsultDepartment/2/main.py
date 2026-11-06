###########################################################################################

### 同一导入需要的依赖库

import os
import sys

import json
from typing import Dict, Any, Union

import shutil

import pandas as pd
from openpyxl import load_workbook, Workbook

import logging
from datetime import datetime

# from pathlib import Path

from win32com.client import Dispatch

import tkinter as tk
from tkinter import filedialog

###########################################################################################

# import logging
# from datetime import datetime

class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        temp_linebuf = self.linebuf + buf
        self.linebuf = ''
        for line in temp_linebuf.splitlines(True):
            if line[-1] == '\n':
                self.logger.log(self.level, line.rstrip())
                sys.__stdout__.write(line)
            else:
                self.linebuf = line
                sys.__stdout__.write(line)

    def flush(self):
        if self.linebuf != '':
            self.logger.log(self.level, self.linebuf.rstrip())
            self.linebuf = ''
        sys.__stdout__.flush()

def setup_logging():
    """
    设置日志记录，将所有print输出同时写入日志文件和控制台
    """
    # 创建logs目录（如果不存在）
    log_dir = os.path.join(get_base_path(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 生成日志文件名（使用当前时间）
    log_filename = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
        ]
    )

    # 创建logger
    logger = logging.getLogger()

    # 重定向stdout和stderr到日志
    sys.stdout = LoggerWriter(logger, logging.INFO)
    sys.stderr = LoggerWriter(logger, logging.ERROR)

    return log_filename

# import os

def file_Move_OR_Copy(source_file_path, target_path, operation="copy"):
    """
    将指定路径源文件复制或者移动到指定目标路径

    参数:
    source_file_path (str): 操作源文件路径（即 所在路径+文件名），不能为空。同时支持相对路径和绝对路径的输入。
    target_path (str): 目标文件路径（路径名），不能为空。同时支持相对路径和绝对路径的输入。
    operation (str): 操作方式选择，"copy"表示复制，"move"表示移动。默认为复制。

    返回:
    bool: 操作成功返回True，失败返回False
    """
    try:
        # 步骤1: 参数验证和路径检查
        # 检查源文件路径是否为空
        if not source_file_path or not isinstance(source_file_path, str):
            raise ValueError("源文件路径不能为空")

        # 检查源文件是否存在
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"源文件不存在: {source_file_path}")
        print(f"*** 存在路径-{source_file_path}")

        # 检查目标路径参数是否为空
        if not target_path or not isinstance(target_path, str):
            raise ValueError("目标路径不能为空")

        # 检查目标路径是否存在，不存在则尝试创建
        if not os.path.exists(target_path):
            try:
                # 如果是目录路径，则创建目录
                os.makedirs(target_path)
                print(f"*** 已创建路径-{target_path}")
            except Exception as e:
                raise Exception(f"无法创建目标路径: {target_path}")
        else:
            print(f"*** 存在路径-{target_path}")

        # 获取源文件名
        source_filename = os.path.basename(source_file_path)

        # 构建目标文件完整路径
        target_file_path = os.path.join(target_path, source_filename)

        # 步骤2: 根据操作方式执行复制或移动操作
        if operation.lower() == "copy":
            # 执行复制操作
            # import shutil
            shutil.copy2(source_file_path, target_file_path)
            # 步骤3: 输出操作结果
            print(f"{source_file_path} --copy--> {target_file_path}")
        elif operation.lower() == "move":
            # 执行移动操作
            # import shutil
            shutil.move(source_file_path, target_file_path)
            # 步骤3: 输出操作结果
            print(f"{source_file_path} --move--> {target_file_path}")
        else:
            raise ValueError("操作方式只能是'copy'或'move'")

        return target_file_path

    except Exception as e:
        print(f"操作失败: {str(e)}")
        return None

# import sys
# import os
# from pathlib import Path

def check_if_bundled():
    """
    检查当前是否运行在PyInstaller打包的环境中

    返回:
        bool: 如果在打包环境中返回True，否则返回False
    """
    try:
        # PyInstaller在打包时会设置sys.frozen为True
        return getattr(sys, 'frozen', False)
    except Exception:
        # 出现异常时，默认返回False（开发环境）
        return False

def get_base_path():
    """
    获取应用程序的基础路径

    返回:
        str: 基础路径字符串
              - 打包环境: 可执行文件所在目录
              - 开发环境: 当前脚本所在目录
    """
    try:
        if getattr(sys, 'frozen', False):
            # 打包环境，返回可执行文件所在目录
            return os.path.dirname(sys.executable)
        else:
            # 开发环境，返回当前脚本所在目录
            return os.path.dirname(os.path.abspath(__file__))
    except Exception as e:
        raise Exception(f"获取基础路径时发生错误: {str(e)}")

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径，适用于开发环境和PyInstaller打包后的环境

    参数:
        relative_path (str): 相对于项目根目录的资源文件路径，例如 "config/settings.json" 或 "images/logo.png"

    返回:
        str: 资源文件的绝对路径

    异常处理:
        FileNotFoundError: 当资源文件不存在时抛出
        Exception: 其他可能的异常
    """
    try:
        # 判断是否处于PyInstaller打包后的环境中
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包后的环境
            base_path = sys._MEIPASS
        else:
            # 开发环境，直接使用当前路径
            base_path = os.path.abspath(".")

        full_path = os.path.join( base_path, relative_path)

        # 检查资源文件是否存在
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"资源文件不存在: {relative_path}")

        # 返回资源文件的绝对路径字符串
        return full_path

    except FileNotFoundError:
        # 文件未找到异常处理
        raise
    except Exception as e:
        # 其他异常处理
        raise Exception(f"获取资源路径时发生错误: {str(e)}")

# import json
# from typing import Dict, Any, Union

def Dict_format_display(
        data: Union[Dict[str, Any], None],
        indent_size: int = 4,
        current_level: int = 0,
        use_color: bool = True,
        use_markdown: bool = False
) -> str:
    """
    格式化多级嵌套字典并返回可读性良好的字符串表示形式

    Args:
        data: 待格式化输出的源数据，为任意层级的嵌套字典，也允许为空
        indent_size: 缩进空格数，为int整数类型，不能小于0
        current_level: 当前处理层级（递归参数），为int整数类型，不能小于0
        use_color: 是否需要ANSI颜色支持
        use_markdown: 是否需要Markdown格式输出

    Returns:
        str: 格式化后的字符串

    Raises:
        TypeError: 当参数类型不正确时抛出
        ValueError: 当参数值不合法时抛出
    """
    try:
        # 参数验证
        if not isinstance(indent_size, int) or indent_size < 0:
            raise ValueError("缩进空格数必须是非负整数")

        if not isinstance(current_level, int) or current_level < 0:
            raise ValueError("当前处理层级必须是非负整数")

        if not isinstance(use_color, bool):
            raise TypeError("是否需要ANSI颜色支持参数必须是布尔值")

        if not isinstance(use_markdown, bool):
            raise TypeError("是否需要Markdown格式输出参数必须是布尔值")

        # 处理空数据情况
        if data is None:
            return ""

        # 确保数据是字典类型
        if not isinstance(data, dict):
            raise TypeError("输入数据必须是字典类型")

        # 定义ANSI颜色代码
        class Colors:
            RED = '\033[31m'
            GREEN = '\033[32m'
            YELLOW = '\033[33m'
            BLUE = '\033[34m'
            MAGENTA = '\033[35m'
            CYAN = '\033[36m'
            WHITE = '\033[37m'
            BOLD = '\033[1m'
            RESET = '\033[0m'

        # 根据层级选择颜色的函数
        def get_color_by_level(level: int) -> str:
            """根据层级深度返回对应颜色"""
            colors = [Colors.BLUE, Colors.GREEN, Colors.YELLOW, Colors.CYAN, Colors.MAGENTA]
            return colors[level % len(colors)]

        # 初始化结果字符串
        result = ""

        # 计算当前层级的缩进
        indent = " " * (current_level * indent_size)

        # 遍历字典中的每个键值对
        for key, value in data.items():
            # 判断是否为嵌套字典
            if isinstance(value, dict):
                # 如果是空字典，按照规范输出
                if len(value) == 0:
                    if use_color:
                        color = get_color_by_level(current_level)
                        reset = Colors.RESET
                        result += f"{indent}{color}<> {key}{reset}: {{}}\n"
                    else:
                        result += f"{indent}<> {key}: {{}}\n"
                else:
                    # 非空字典作为分支节点处理
                    if use_color:
                        color = get_color_by_level(current_level)
                        reset = Colors.RESET
                        result += f"{indent}{color}-> {key}:{reset}\n"
                    else:
                        result += f"{indent}-> {key}:\n"
                    # 递归处理子字典，层级加1
                    result += Dict_format_display(
                        value,
                        indent_size,
                        current_level + 1,
                        use_color,
                        use_markdown
                    )
            else:
                # 终端节点，直接输出键值对
                if use_color:
                    key_color = get_color_by_level(current_level)
                    value_color = Colors.WHITE
                    reset = Colors.RESET
                    result += f"{indent}{key_color}···· {key}:{reset} {value_color}{value}{reset}\n"
                else:
                    result += f"{indent}···· {key}: {value}\n"

        return result

    except Exception as e:
        # 异常处理
        raise RuntimeError(f"格式化字典时发生错误: {str(e)}")

# import os
# import json

def Json_Check_Read(name, json_path):
    """
    从指定json文件读取参数内容并进行对比，如果对比结果合法则将读取的内容格式化为dict字典并返回

    Args:
        name (str): 用户输入的方案名称，不能为空
        json_path (str): 需要读取的json文件路径（所在路径+文件名），不能为空，支持相对路径和绝对路径

    Returns:
        dict: 用户输入对应的顶级键值对的值（嵌套字典）

    Raises:
        ValueError: 当参数为空或不合法时抛出
        FileNotFoundError: 当指定的json文件不存在时抛出
        json.JSONDecodeError: 当json文件格式不正确时抛出
    """
    try:
        # 步骤1: 参数验证
        # 检查第一个参数name是否存在且不为空
        if not name or not isinstance(name, str):
            raise ValueError("用户输入的方案名称不能为空")

        # 检查第二个参数json_path是否存在且不为空
        if not json_path or not isinstance(json_path, str):
            raise ValueError("json文件路径不能为空")

        # 使用os模块判断路径文件是否存在
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"指定的json文件不存在: {json_path}")

        print(f"*** 存在路径-{json_path}")

        # 步骤2: 读取指定json文件的内容
        with open(json_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 提取第一级（最高层级）所有键名称为list列表
        first_level_keys = list(config_data.keys())
        print(f"已读取到方案：{first_level_keys}")

        # 步骤3: 对比用户输入与方案名称列表
        if name in first_level_keys:
            # 用户输入匹配，读取对应的嵌套字典
            result_dict = config_data[name]
            print(f"\n >>>>>> 已选择方案：{name} <<<<<< ")

            # 使用Dict_format_display函数格式化显示字典内容
            formatted_output = Dict_format_display(result_dict)
            print(formatted_output)

            # 返回用户输入对应的顶级键值对的值
            return result_dict
        else:
            # 用户输入不匹配，抛出异常
            raise ValueError(f"输入的方案名称 '{name}' 与配置文件中的方案不匹配")

    except FileNotFoundError:
        raise FileNotFoundError(f"找不到指定的json文件: {json_path}")
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"处理过程中发生未知错误: {str(e)}")

# import os

def create_folder(folder_name, target_path=None):
    # 步骤1：验证文件夹名称
    if not folder_name:
        raise ValueError("文件夹名称不能为空")  # 如果文件夹名称为空，抛出异常

    # 步骤2：确定要创建文件夹的完整路径
    if not target_path:
        # 如果没有提供目标路径，则使用当前脚本所在的目录
        target_path = os.getcwd()  # 获取当前工作目录
    else:
        # 检查提供的目标路径是否存在
        if not os.path.exists(target_path):
            try:
                # 如果目标路径不存在，则尝试创建该路径
                os.makedirs(target_path)  # 创建所有中间级目录以包含叶目录
            except Exception as e:
                print(f"创建目标路径时出错: {e}")  # 打印错误信息如果路径创建失败
                return False  # 返回False表示失败

    # 新文件夹的完整路径
    full_path = os.path.join(target_path, folder_name)  # 将目标路径和文件夹名称连接形成完整路径

    # 步骤3：在指定路径下创建文件夹
    try:
        os.mkdir(full_path)  # 尝试在指定路径下创建目录
        print(f"文件夹 '{folder_name}' 成功创建于 '{full_path}'")  # 打印成功消息
        return True  # 返回True表示成功
    except FileExistsError:
        print(f"文件夹 '{folder_name}' 已经存在于 '{full_path}'")  # 打印消息如果文件夹已经存在
        return False  # 返回False表示失败
    except PermissionError:
        print(f"权限被拒绝: 无法在 '{full_path}' 创建文件夹 '{folder_name}'")  # 打印消息如果权限被拒绝
        return False  # 返回False表示失败
    except Exception as e:
        print(f"创建文件夹 '{folder_name}' 时发生错误: {e}")  # 打印任何其他发生的异常
        return False  # 返回False表示失败

# import os
# import json

def XLS_to_XLSX(source_file_path, target_folder_path=None):
    """
    将指定的.xls格式Excel文件转换为.xlsx格式Excel文件并保存到指定地址

    该函数在Windows系统环境下，接收.xls格式Excel源文件路径和目标文件夹路径，
    将源文件转换为.xlsx格式并保存到指定位置。

    参数:
        source_file_path (str): 需要转换的.xls格式Excel源文件的文件路径名（路径+文件名）
                               支持相对路径和绝对路径
        target_folder_path (str): 转换后.xlsx格式Excel文件保存的目标文件夹路径
                                 支持相对路径和绝对路径，如果为空则默认保存到源文件相同目录下

    返回:
        str: 转换成功后保存的文件路径，如果失败则返回None

    异常:
        ValueError: 当源文件路径为空时抛出
        FileNotFoundError: 当源文件不存在时抛出
        Exception: 其他转换过程中发生的异常
    """
    try:
        # 步骤1: 参数验证和路径检查
        # 检查第一个参数source_file_path是否存在且不为空
        if not source_file_path or not isinstance(source_file_path, str):
            raise ValueError("源文件路径不能为空")

        # 检查源文件是否存在
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"源文件不存在: {source_file_path}")
        print(f"*** 存在路径-{source_file_path}")

        # 获取源文件所在的目录
        source_dir = os.path.dirname(source_file_path)

        # 处理目标文件夹路径参数
        if not target_folder_path or not isinstance(target_folder_path, str):
            # 如果目标文件夹路径为空，则默认为源文件所在的目录
            target_folder_path = source_dir
            print(f"*** 使用默认路径-{target_folder_path}")
        else:
            # 检查目标文件夹是否存在，不存在则尝试创建
            if not os.path.exists(target_folder_path):
                try:
                    os.makedirs(target_folder_path)
                    print(f"*** 已创建路径-{target_folder_path}")
                except Exception as e:
                    raise Exception(f"无法创建目标路径: {target_folder_path}")
            else:
                print(f"*** 存在路径-{target_folder_path}")

        # 步骤2: 构建目标文件路径
        # 获取源文件名（不含扩展名）
        base_name = os.path.splitext(os.path.basename(source_file_path))[0]
        # 构建目标文件完整路径（.xlsx格式）
        destination_file_path = os.path.join(target_folder_path, f"{base_name}.xlsx")

        # 步骤3: 使用Excel应用程序进行文件转换
        # 创建Excel应用程序对象
        excel_app = Dispatch("Excel.Application")

        try:
            # 打开.xls源文件
            workbook = excel_app.Workbooks.Open(source_file_path)
            print(f"*** 存在数据表-{os.path.basename(source_file_path)}")

            # 保存为.xlsx格式文件（FileFormat=51表示xlsx格式）
            workbook.SaveAs(destination_file_path, FileFormat=51)
            workbook.Close()

            # 打印操作结果
            print(f" ··· {os.path.basename(source_file_path)} -> XLSX :: {destination_file_path}")

            # 返回成功保存的路径地址
            return destination_file_path

        except Exception as e:
            # 转换过程中发生异常
            print(f"转换失败: {e}")
            return None
        finally:
            # 确保Excel应用程序被退出
            excel_app.Quit()

    except Exception as e:
        # 处理其他可能的异常
        print(f"函数执行过程中发生错误: {e}")
        return None

def menu_Printf():
    """
    显示数据读取方式选择菜单并获取用户输入

    该函数会在Windows系统环境下清屏，然后显示功能菜单引导用户输入一个1-4之间的整数进行选择，
    并将该输入数字返回。如果输入范围不在1~4中，则提示用户并要求重新输入。
    如果出现任何导致函数功能不能正常进行的情况，则中断跳出并返回0。

    菜单选项:
    1 - 直接输入数据内容
    2 - 输入文件路径名（支持相对路径和绝对路径）
    3 - 调用文件选择对话框选择文件（支持多选）
    4 - 结束输入

    Returns:
        int: 用户选择的选项编号(1-4)，如果出现异常则返回0
    """
    try:
        # 清屏操作，兼容Windows和Unix系统
        os.system('cls' if os.name == 'nt' else 'clear')

        # 显示选择菜单，格式化为易于阅读的格式
        print("==========================================")
        print("           数据读取方式选择菜单           ")
        print("==========================================")
        print("  1. 直接输入数据内容")
        print("  2. 输入文件路径名")
        print("  3. 调用文件选择对话框")
        print("  4. 结束输入")
        print("==========================================")

        # 循环读取用户输入直到输入有效值
        while True:
            # 读取用户输入并去除首尾空格
            user_choice = input("请选择数据读取方式 (1-4): ").strip()

            # 检查输入是否为空
            if not user_choice:
                print("输入不能为空，请输入1-4之间的数字。")
                continue

            # 将输入转换为整数
            choice_num = int(user_choice)

            # 检查输入是否为数字
            if not user_choice.isdigit():
                print("输入无效，请输入1-4之间的数字。")
                continue

            # 检查输入范围是否在1-4之间
            if 1 <= choice_num <= 4:
                # 输入有效，返回选择的数字
                return choice_num
            else:
                # 输入超出范围，提示用户重新输入
                print("输入超出范围，请输入1-4之间的数字。")
                continue

    except KeyboardInterrupt:
        # 处理用户中断（如Ctrl+C）
        print("\n操作被用户中断。")
        return 0
    except Exception as e:
        # 处理其他可能的异常
        print(f"函数执行过程中发生错误: {e}")
        return 0

def string_Read():
    """
    引导用户输入内容字符串并进行解析，将解析后的结果以列表形式返回

    该函数会在Windows系统环境下引导用户输入内容字符串，按照空格分隔的格式解析字符串，
    每个非空子字符串作为一个元素添加到结果列表中，并将结果返回。
    如果出现任何导致函数功能不能正常进行的情况，则中断跳出并返回None。

    具体操作步骤:
    1. 初始化一个空list列表用于存储结果
    2. 输出提示告知用户格式规范（任意两个相邻元素之间通过空格分隔）
    3. 读取用户输入的字符串并按空格分割
    4. 每个非空子字符串作为list列表的一个元素添加到结果列表中
    5. 返回最终的读取结果list列表

    Returns:
        list: 解析后的字符串元素列表，如果出现异常则返回None
    """
    try:
        # 步骤1: 初始化一个空list列表用于存储结果
        result_list = []

        # 步骤2: 输出提示告知用户格式规范，引导用户输入内容
        print("请输入数据内容（多个元素请用空格分隔）:")
        data_content = input().strip()

        # 检查输入是否为空
        if not data_content:
            print("输入内容为空")
            return result_list

        # 步骤3: 按空格分割字符串
        # split()方法会自动处理多个连续空格的情况，并去除首尾空格
        substrings = data_content.split()

        # 步骤4: 遍历分割后的子字符串，将非空字符串添加到结果列表中
        for substring in substrings:
            # 确保子字符串非空（split()已经处理了这种情况，但为了安全起见再次检查）
            if substring:
                result_list.append(substring)
                # 每成功分割并存储一个有效子字符串，打印结果
                print(f" · 已从输入读取到内容 -> {substring}")

        # 步骤5: 打印总结信息
        print(f"\n --> 总计读取到 {len(result_list)} 个元素，具体有：")
        print(f" {result_list}\n")

        # 返回最终的读取结果list列表
        return result_list

    except KeyboardInterrupt:
        # 处理用户中断（如Ctrl+C）
        print("\n操作被用户中断。")
        return None
    except Exception as e:
        # 处理其他可能的异常
        print(f"函数执行过程中发生错误: {e}")
        return None

### "File_read" Version-1.0
# def File_Read():
#     """
#     引导用户输入文件路径名并据此对指定的excel文件或者txt文本文件进行解析，并将解析后的结果以列表形式返回
#
#     该函数在Windows系统环境下，引导用户输入文件路径名（支持相对路径和绝对路径），
#     并根据文件类型进行相应的解析处理，最终将结果以列表形式返回。
#
#     具体操作步骤:
#     1. 初始化一个空list列表用于存储结果
#     2. 输出提示告知用户文件路径规范，引导用户输入文件路径名
#     3. 解析字符串所指代的文件，判断文件是否存在和格式是否合法
#     4. 根据文件类型进行相应处理：
#        - txt文件：按行读取内容
#        - xls文件：转换为xlsx后读取相关内容
#        - xlsx文件：直接读取相关内容
#     5. 返回最终的读取结果list列表
#
#     Returns:
#         list: 解析后的文件内容列表，如果出现异常则返回None
#     """
#     try:
#         # 步骤1: 初始化一个空list列表用于存储结果
#         result_list = []
#
#         # 步骤2: 输出提示告知用户文件路径规范，引导用户输入文件路径名
#         print("请输入文件路径 (支持相对路径和绝对路径，支持的文件格式：.txt, .xls, .xlsx):")
#         file_path = input().strip()
#
#         # 检查输入是否为空
#         if not file_path:
#             print("文件路径为空")
#             return None
#
#         # 步骤3: 解析文件路径并验证文件
#         # 使用os模块判断路径文件是否存在
#         if not os.path.exists(file_path):
#             print(f"文件不存在: {file_path}")
#             return None
#
#         # 获取文件扩展名并转换为小写以便比较
#         _, file_extension = os.path.splitext(file_path)
#         file_extension = file_extension.lower()
#
#         # 检查文件扩展名是否符合要求
#         if file_extension not in ['.txt', '.xls', '.xlsx']:
#             print(f"不支持的文件格式: {file_extension}，仅支持 .txt, .xls, .xlsx 格式")
#             return None
#
#         # 获取文件名（不含路径）
#         file_name = os.path.basename(file_path)
#         print(f" *** {file_name} -> 存在 || 识别为 {file_extension[1:]} 格式 -> 合法 --------")
#
#         # 步骤4: 根据文件类型进行解析
#         if file_extension == '.txt':
#             # txt文本文件处理
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 lines = f.readlines()
#                 for line in lines:
#                     # 去除行尾换行符并添加到结果列表
#                     content = line.rstrip('\n')
#                     if content:  # 只添加非空行
#                         result_list.append(content)
#                         print(f" · 已从文本文件读取到内容 -> {content}")
#
#         elif file_extension == '.xls':
#             # xls格式excel文件处理
#             # 先调用XLS_to_XLSX函数转换文件
#             converted_file_path = XLS_to_XLSX(file_path)
#
#             if not converted_file_path:
#                 print("XLS文件转换失败")
#                 return None
#
#             # 调用file_Move_OR_Copy函数将转换后的文件移动到./temp文件夹中
#             temp_file_path = file_Move_OR_Copy(converted_file_path, "./temp", "move")
#
#             if not temp_file_path:
#                 print("移动转换后的文件失败")
#                 return None
#
#             # 读取xlsx文件中的相关内容
#             excel_file_path = temp_file_path
#             # 读取所有工作表
#             excel_file = pd.ExcelFile(excel_file_path)
#
#             # 遍历所有工作表
#             for sheet_name in excel_file.sheet_names:
#                 # 读取工作表数据
#                 df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
#
#                 # 查找相关表头（包含"人员"、"姓名"、"名称"、"名"的列）
#                 target_columns = []
#                 for column in df.columns:
#                     column_str = str(column)
#                     if any(keyword in column_str for keyword in ["人员", "姓名", "名称", "名"]):
#                         target_columns.append(column)
#
#                 # 读取目标列的数据
#                 for column in target_columns:
#                     # 将该列的所有非空值添加到结果列表中
#                     column_data = df[column].dropna()  # 去除空值
#                     for value in column_data:
#                         value_str = str(value).strip()
#                         if value_str:  # 只添加非空字符串
#                             result_list.append(value_str)
#                             print(f" · 已从Excel文件{sheet_name}工作表读取到内容 -> {value_str}")
#
#         elif file_extension == '.xlsx':
#             # xlsx格式excel文件处理
#             # 读取所有工作表
#             excel_file = pd.ExcelFile(file_path)
#
#             # 遍历所有工作表
#             for sheet_name in excel_file.sheet_names:
#                 # 读取工作表数据
#                 df = pd.read_excel(file_path, sheet_name=sheet_name)
#
#                 # 查找相关表头（包含"人员"、"姓名"、"名称"、"名"的列）
#                 target_columns = []
#                 for column in df.columns:
#                     column_str = str(column)
#                     if any(keyword in column_str for keyword in ["人员", "姓名", "名称", "名"]):
#                         target_columns.append(column)
#
#                 # 读取目标列的数据
#                 for column in target_columns:
#                     # 将该列的所有非空值添加到结果列表中
#                     column_data = df[column].dropna()  # 去除空值
#                     for value in column_data:
#                         value_str = str(value).strip()
#                         if value_str:  # 只添加非空字符串
#                             result_list.append(value_str)
#                             print(f" · 已从Excel文件{sheet_name}工作表读取到内容 -> {value_str}")
#
#         # 步骤5: 返回最终的读取结果list列表
#         print(f"\n --> 总计读取到 {len(result_list)} 个元素，具体有：")
#         print(f" {result_list}\n")
#
#         return result_list
#
#     except KeyboardInterrupt:
#         # 处理用户中断（如Ctrl+C）
#         print("\n操作被用户中断。")
#         return None
#     except Exception as e:
#         # 处理其他可能的异常
#         print(f"函数执行过程中发生错误: {e}")
#         return None

### "File_read" Version-2.0
# def File_Read(file_paths=None):
#     """
#     引导用户输入文件路径名或直接处理传入的文件路径列表，并据此对指定的excel文件或者txt文本文件进行解析，并将解析后的结果以列表形式返回
#
#     该函数在Windows系统环境下，可以接收文件路径列表参数，如果参数为空则引导用户输入文件路径，
#     否则直接处理参数中的文件路径列表，根据文件类型进行相应的解析处理，最终将结果以列表形式返回。
#
#     参数:
#         file_paths (list): 可选，文件路径列表。如果为空或不存在，则引导用户输入文件路径。
#
#     具体操作步骤:
#     1. 初始化一个空list列表用于存储结果和一个临时空list列表用于存储文件路径地址
#     2. 检查参数，如果参数不为空则将参数输入的list列表添加到临时路径list列表中，然后直接进入第3步
#     3. 否则输出提示告知用户文件路径规范，引导用户输入文件路径名并读取输入的字符串，并将其添加到临时路径list列表中
#     4. 对临时路径list列表逐一扫描检查字符串元素所指代的文件，判断文件是否存在和格式是否合法
#     5. 逐一对其字符串元素所指代的文件进行读取解析
#     6. 返回最终的读取结果list列表
#
#     Returns:
#         list: 解析后的文件内容列表，如果出现异常则返回None
#     """
#     try:
#         # 步骤1: 初始化一个空list列表用于存储结果和一个临时空list列表用于存储文件路径地址
#         result_list = []  # 用于存储最终解析结果
#         temp_file_paths = []  # 用于存储待处理的文件路径
#
#         # 检查参数，如果参数不为空则将参数输入的list列表添加到临时路径list列表中
#         if file_paths and isinstance(file_paths, list) and len(file_paths) > 0:
#             # 参数不为空，将参数中的文件路径添加到临时路径列表中
#             temp_file_paths.extend(file_paths)
#             print(f"已接收 {len(file_paths)} 个文件路径作为输入")
#         else:
#             # 步骤2: 输出提示告知用户文件路径规范，引导用户输入文件路径名并读取输入的字符串
#             print("请输入文件路径 (支持相对路径和绝对路径，支持的文件格式：.txt, .xls, .xlsx):")
#             input_file_path = input().strip()
#
#             # 检查输入是否为空
#             if not input_file_path:
#                 print("文件路径为空")
#                 return None
#
#             # 将用户输入的文件路径添加到临时路径列表中
#             temp_file_paths.append(input_file_path)
#
#         # 步骤3: 对临时路径list列表逐一扫描检查字符串元素所指代的文件
#         for file_path in temp_file_paths:
#             # 使用os模块判断路径文件是否存在
#             if not os.path.exists(file_path):
#                 print(f"文件不存在: {file_path}")
#                 return None
#
#             # 获取文件扩展名并转换为小写以便比较
#             _, file_extension = os.path.splitext(file_path)
#             file_extension = file_extension.lower()
#
#             # 检查文件扩展名是否符合要求
#             if file_extension not in ['.txt', '.xls', '.xlsx']:
#                 print(f"不支持的文件格式: {file_extension}，仅支持 .txt, .xls, .xlsx 格式")
#                 return None
#
#             # 获取文件名（不含路径）
#             file_name = os.path.basename(file_path)
#             print(f" *** {file_name} -> 存在 || 识别为 {file_extension[1:]} 格式 -> 合法 --------")
#
#         # 步骤4: 临时路径list列表遍历检查合法后，逐一对其字符串元素所指代的文件进行读取解析
#         for file_path in temp_file_paths:
#             # 获取文件扩展名并转换为小写以便比较
#             _, file_extension = os.path.splitext(file_path)
#             file_extension = file_extension.lower()
#
#             # 根据文件类型进行解析
#             if file_extension == '.txt':
#                 # txt文本文件处理
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     lines = f.readlines()
#                     for line in lines:
#                         # 去除行尾换行符并添加到结果列表
#                         content = line.rstrip('\n')
#                         if content:  # 只添加非空行
#                             result_list.append(content)
#                             print(f" · 已从文本文件读取到内容 -> {content}")
#
#             elif file_extension == '.xls':
#                 # xls格式excel文件处理
#                 # 先调用XLS_to_XLSX函数转换文件
#                 converted_file_path = XLS_to_XLSX(file_path)
#
#                 if not converted_file_path:
#                     print("XLS文件转换失败")
#                     return None
#
#                 # 调用file_Move_OR_Copy函数将转换后的文件移动到./temp文件夹中
#                 temp_file_path = file_Move_OR_Copy(converted_file_path, "./temp", "move")
#
#                 if not temp_file_path:
#                     print("移动转换后的文件失败")
#                     return None
#
#                 # 读取xlsx文件中的相关内容
#                 excel_file_path = temp_file_path
#                 # 读取所有工作表
#                 excel_file = pd.ExcelFile(excel_file_path)
#
#                 # 遍历所有工作表
#                 for sheet_name in excel_file.sheet_names:
#                     # 读取工作表数据
#                     df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
#
#                     # 查找相关表头（包含"人员"、"姓名"、"名称"、"名"的列）
#                     target_columns = []
#                     for column in df.columns:
#                         column_str = str(column)
#                         if any(keyword in column_str for keyword in ["人员", "姓名", "名称", "名"]):
#                             target_columns.append(column)
#
#                     # 读取目标列的数据
#                     for column in target_columns:
#                         # 将该列的所有非空值添加到结果列表中
#                         column_data = df[column].dropna()  # 去除空值
#                         for value in column_data:
#                             value_str = str(value).strip()
#                             if value_str:  # 只添加非空字符串
#                                 result_list.append(value_str)
#                                 print(f" · 已从Excel文件{sheet_name}工作表读取到内容 -> {value_str}")
#
#             elif file_extension == '.xlsx':
#                 # xlsx格式excel文件处理
#                 # 读取所有工作表
#                 excel_file = pd.ExcelFile(file_path)
#
#                 # 遍历所有工作表
#                 for sheet_name in excel_file.sheet_names:
#                     # 读取工作表数据
#                     df = pd.read_excel(file_path, sheet_name=sheet_name)
#
#                     # 查找相关表头（包含"人员"、"姓名"、"名称"、"名"的列）
#                     target_columns = []
#                     for column in df.columns:
#                         column_str = str(column)
#                         if any(keyword in column_str for keyword in ["人员", "姓名", "名称", "名"]):
#                             target_columns.append(column)
#
#                     # 读取目标列的数据
#                     for column in target_columns:
#                         # 将该列的所有非空值添加到结果列表中
#                         column_data = df[column].dropna()  # 去除空值
#                         for value in column_data:
#                             value_str = str(value).strip()
#                             if value_str:  # 只添加非空字符串
#                                 result_list.append(value_str)
#                                 print(f" · 已从Excel文件{sheet_name}工作表读取到内容 -> {value_str}")
#
#         # 步骤5: 返回最终的读取结果list列表
#         print(f"\n --> 总计读取到 {len(result_list)} 个元素，具体有：")
#         print(f" {result_list}\n")
#
#         return result_list
#
#     except KeyboardInterrupt:
#         # 处理用户中断（如Ctrl+C）
#         print("\n操作被用户中断。")
#         return None
#     except Exception as e:
#         # 处理其他可能的异常
#         print(f"函数执行过程中发生错误: {e}")
#         return None

### "File_read" Version-3.0
def File_Read(file_paths=None):
    """
    引导用户输入文件路径名或直接处理传入的文件路径列表，并据此对指定的excel文件或者txt文本文件进行解析，并将解析后的结果以列表形式返回

    该函数在Windows系统环境下，可以接收文件路径列表参数，如果参数为空则引导用户输入文件路径，
    否则直接处理参数中的文件路径列表，根据文件类型进行相应的解析处理，最终将结果以列表形式返回。

    参数:
        file_paths (list): 可选，文件路径列表。如果为空或不存在，则引导用户输入文件路径。

    具体操作步骤:
    1. 初始化一个空list列表用于存储结果和一个临时空list列表用于存储文件路径地址
    2. 检查参数，如果参数不为空则将参数输入的list列表添加到临时路径list列表中，然后直接进入第3步
    3. 否则输出提示告知用户文件路径规范，引导用户输入文件路径名并读取输入的字符串，并将其添加到临时路径list列表中
    4. 对临时路径list列表逐一扫描检查字符串元素所指代的文件，判断文件是否存在和格式是否合法
    5. 逐一对其字符串元素所指代的文件进行读取解析
    6. 返回最终的读取结果list列表

    Returns:
        list: 解析后的文件内容列表，如果出现异常则返回None
    """
    try:
        # 步骤1: 初始化一个空list列表用于存储结果和一个临时空list列表用于存储文件路径地址
        result_list = []  # 用于存储最终解析结果
        temp_file_paths = []  # 用于存储待处理的文件路径

        # 检查参数，如果参数不为空则将参数输入的list列表添加到临时路径list列表中
        if file_paths and isinstance(file_paths, list) and len(file_paths) > 0:
            # 参数不为空，将参数中的文件路径添加到临时路径列表中
            temp_file_paths.extend(file_paths)
            print(f"已接收 {len(file_paths)} 个文件路径作为输入")
        else:
            # 步骤2: 输出提示告知用户文件路径规范，引导用户输入文件路径名并读取输入的字符串
            print("请输入文件路径 (支持相对路径和绝对路径，支持的文件格式：.txt, .xls, .xlsx):")
            print("路径格式规范:")
            print("  绝对路径示例: C:\\Users\\用户名\\Documents\\example.txt")
            print("  相对路径示例: .\\folder\\example.txt 或 ../folder/example.txt")
            input_file_path = input().strip()

            # 检查输入是否为空
            if not input_file_path:
                print("文件路径为空")
                return None

            # 将用户输入的文件路径添加到临时路径列表中
            temp_file_paths.append(input_file_path)

        # 步骤3: 对临时路径list列表逐一扫描检查字符串元素所指代的文件
        for file_path in temp_file_paths:
            # 使用os模块判断路径文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return None

            # 获取文件扩展名并转换为小写以便比较
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            # 检查文件扩展名是否符合要求
            if file_extension not in ['.txt', '.xls', '.xlsx']:
                print(f"不支持的文件格式: {file_extension}，仅支持 .txt, .xls, .xlsx 格式")
                return None

            # 获取文件名（不含路径）
            file_name = os.path.basename(file_path)
            print(f" *** {file_name} -> 存在 || 识别为 {file_extension[1:]} 格式 -> 合法 --------")

        # 步骤4: 临时路径list列表遍历检查合法后，逐一对其字符串元素所指代的文件进行读取解析
        for file_path in temp_file_paths:
            # 获取文件扩展名并转换为小写以便比较
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()

            # 根据文件类型进行解析
            if file_extension == '.txt':
                # txt文本文件处理
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        # 去除行尾换行符并添加到结果列表
                        content = line.rstrip('\n')
                        if content:  # 只添加非空行
                            result_list.append(content)
                            print(f" · 已从文本文件读取到内容 -> {content}")

            elif file_extension == '.xls':
                # xls格式excel文件处理
                # 先调用XLS_to_XLSX函数转换文件
                converted_file_path = XLS_to_XLSX(file_path)

                if not converted_file_path:
                    print("XLS文件转换失败")
                    return None

                # 调用file_Move_OR_Copy函数将转换后的文件移动到./temp文件夹中
                temp_file_path = file_Move_OR_Copy(converted_file_path, "./temp", "move")

                if not temp_file_path:
                    print("移动转换后的文件失败")
                    return None

                # 读取xlsx文件中的相关内容
                excel_file_path = temp_file_path
                # 读取所有工作表
                excel_file = pd.ExcelFile(excel_file_path)

                # 遍历所有工作表
                for sheet_name in excel_file.sheet_names:
                    # 读取工作表数据
                    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

                    # 查找相关表头（包含"人员"、"姓名"、"名称"、"名"的列）
                    target_columns = []
                    for column in df.columns:
                        column_str = str(column)
                        if any(keyword in column_str for keyword in ["人员", "姓名", "名称", "名"]):
                            target_columns.append(column)

                    # 读取目标列的数据
                    for column in target_columns:
                        # 将该列的所有非空值添加到结果列表中
                        column_data = df[column].dropna()  # 去除空值
                        for value in column_data:
                            value_str = str(value).strip()
                            if value_str:  # 只添加非空字符串
                                # 使用正则表达式分割字符串，支持中英文空格字符
                                import re
                                # 分割符包括：空格、退格、换行符、TAB、逗号、句号、分号、顿号、左斜杠、右斜杠等
                                sub_strings = re.split(r'[\s\,\.\;\、\，\。\；\\\/]+', value_str)
                                for sub_str in sub_strings:
                                    sub_str = sub_str.strip()
                                    if sub_str:  # 只添加非空字符串
                                        result_list.append(sub_str)
                                        print(f" · 已从输入读取到内容 -> {sub_str}")

            elif file_extension == '.xlsx':
                # xlsx格式excel文件处理
                # 读取所有工作表
                excel_file = pd.ExcelFile(file_path)

                # 遍历所有工作表
                for sheet_name in excel_file.sheet_names:
                    # 读取工作表数据
                    df = pd.read_excel(file_path, sheet_name=sheet_name)

                    # 查找相关表头（包含"人员"、"姓名"、"名称"、"名"的列）
                    target_columns = []
                    for column in df.columns:
                        column_str = str(column)
                        if any(keyword in column_str for keyword in ["人员", "姓名", "名称", "名"]):
                            target_columns.append(column)

                    # 读取目标列的数据
                    for column in target_columns:
                        # 将该列的所有非空值添加到结果列表中
                        column_data = df[column].dropna()  # 去除空值
                        for value in column_data:
                            value_str = str(value).strip()
                            if value_str:  # 只添加非空字符串
                                # 使用正则表达式分割字符串，支持中英文空格字符
                                import re
                                # 分割符包括：空格、退格、换行符、TAB、逗号、句号、分号、顿号、左斜杠、右斜杠等
                                sub_strings = re.split(r'[\s\,\.\;\、\，\。\；\\\/]+', value_str)
                                for sub_str in sub_strings:
                                    sub_str = sub_str.strip()
                                    if sub_str:  # 只添加非空字符串
                                        result_list.append(sub_str)
                                        print(f" · 已从输入读取到内容 -> {sub_str}")

        # 步骤5: 返回最终的读取结果list列表
        print(f"\n --> 总计读取到 {len(result_list)} 个元素，具体有：")
        print(f" {result_list}\n")

        return result_list

    except KeyboardInterrupt:
        # 处理用户中断（如Ctrl+C）
        print("\n操作被用户中断。")
        return None
    except Exception as e:
        # 处理其他可能的异常
        print(f"函数执行过程中发生错误: {e}")
        return None


def Windows_File_select():
    """
    调用Windows系统原生的文件选择对话框通过图形化界面交互的方式选择文件，并返回被选择的文件路径list列表

    该函数在Windows系统环境下，调用系统原生的文件选择对话框供用户选择文件，
    支持单次操作时在同一文件夹内同时选择多个文件，并对选择的文件进行验证。

    具体操作步骤:
    1. 初始化一个空list列表用于存储结果
    2. 调用Windows系统原生的文件选择对话框，支持多选文件
    3. 对选中的文件路径进行验证，检查文件是否存在且格式是否符合要求
    4. 返回最终的读取结果list列表

    Returns:
        list: 选中且验证通过的文件路径列表，如果出现异常则返回None
    """
    try:
        # 步骤1: 初始化一个空list列表用于存储结果
        result_list = []

        # 步骤2: 调用Windows系统原生的文件选择对话框
        # 使用tkinter创建文件选择对话框
        # 隐藏主窗口
        root = tk.Tk()
        root.withdraw()
        root.update()  # 强制刷新GUI，确保对话框能正常显示

        # 设置对话框属性，支持多选文件
        file_paths = filedialog.askopenfilenames(
            title="请选择需要读取的文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("文本文件", "*.txt"),
                ("Excel文件", "*.xlsx;*.xls"),
                ("JSON文件", "*.json"),
                ("CSV文件", "*.csv")
            ]
        )

        # 销毁主窗口
        root.destroy()

        # 检查是否有选择文件
        if not file_paths:
            print("未选择任何文件")
            return None

        # 将选中的文件路径添加到结果列表中
        result_list.extend(file_paths)
        print(f"已选择 {len(file_paths)} 个文件")

        # 步骤3: 对结果列表中的每个文件路径进行验证
        # 创建一个临时列表用于存储需要移除的索引
        invalid_indices = []

        # 遍历结果列表中的每个文件路径
        for i, file_path in enumerate(result_list):
            try:
                # 获取文件名（不含路径）
                file_name = os.path.basename(file_path)

                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f" -- {file_name} :: False  :: {file_path}")
                    logging.error(f"文件不存在: {file_path}")
                    invalid_indices.append(i)
                    continue

                # 获取文件扩展名并转换为小写以便比较
                _, file_extension = os.path.splitext(file_path)
                file_extension = file_extension.lower()

                # 检查文件扩展名是否符合要求（txt、xls、xlsx）
                if file_extension not in ['.txt', '.xls', '.xlsx']:
                    print(f" -- {file_name} :: False  :: {file_path}")
                    logging.error(f"不支持的文件格式: {file_extension}，仅支持 .txt, .xls, .xlsx 格式")
                    invalid_indices.append(i)
                    continue

                # 文件存在且格式符合要求
                print(f" -- {file_name} :: True  :: {file_path}")

            except Exception as e:
                # 处理验证过程中可能发生的异常
                file_name = os.path.basename(file_path) if 'file_path' in locals() else "未知文件"
                print(f" -- {file_name} :: False  :: {file_path}")
                logging.error(f"验证文件时发生错误: {e}")
                invalid_indices.append(i)

        # 从后往前删除无效的文件路径，避免索引变化问题
        for i in reversed(invalid_indices):
            result_list.pop(i)

        # 步骤4: 返回最终的读取结果list列表
        print(f"\n --> 总计读取到 {len(result_list)} 个元素，具体有：")
        print(f" {result_list}\n")

        return result_list if result_list else None

    except KeyboardInterrupt:
        # 处理用户中断（如Ctrl+C）
        print("\n操作被用户中断。")
        return None

    except Exception as e:
        # 处理其他可能的异常
        print(f"函数执行过程中发生错误: {e}")
        logging.error(f"Windows_File_select函数执行过程中发生错误: {e}")
        return None

# import tkinter as tk
# from tkinter import filedialog

def RPA_OPcondition_Read():
    """
    通过多种方式获取数据内容并整理为list列表返回的功能函数

    该函数提供以下功能：
    1. 直接输入数据内容
    2. 通过文件路径读取文件
    3. 通过系统文件选择对话框选择文件
    4. 循环操作直到用户选择结束

    Returns:
        list: 包含读取到的所有数据内容的列表
    """
    try:
        # 初始化操作
        print("*** 初始化:Check 成功")
        result_list = []  # 初始化结果列表
        print("*** 初始化:Init 成功")
        round_num = 0  # 初始化轮次计数器

        while True:
            round_num += 1

            # 调用menu_Printf函数显示菜单并获取用户选择
            user_choice = menu_Printf()

            # 出现异常，主动中断程序
            if user_choice == 0:
                print("\n------------!!! 操作异常 !!!------------\n")
                exit()

            # 如果输入4，则操作结束
            if user_choice == 4:
                print(f" >>> 当前已读取到了 {len(result_list)} 个元素并存储 <<< ")
                return result_list

            # 根据用户选择执行不同操作
            if user_choice == 1:
                # 直接输入数据内容
                try:
                    print("*** 第{}轮-直接输入数据内容 ***".format(round_num))

                    # 调用string_Read函数处理字符串输入
                    data_content_list = string_Read()

                    # 检查输入是否为空
                    if not data_content_list or len(data_content_list) == 0:
                        print(f" *** 第{round_num}轮-1操作_发生错误 |-> 输入内容为空")
                        continue

                    # 将解析后的所有元素添加到结果列表中
                    result_list.extend(data_content_list)
                    print(f" *** 第{round_num}轮-1操作_成功 |-> 数据已添加")

                except Exception as e:
                    print(f" *** 第{round_num}轮-1操作_发生错误 |-> {e} ")
                    continue

            elif user_choice == 2:

                # 输入文件路径名
                try:
                    print("*** 第{}轮-输入文件路径名 ***".format(round_num))

                    # 调用File_Read函数处理文件读取
                    file_content_list = File_Read()

                    # 检查文件读取是否成功
                    if file_content_list is None:
                        print(f" *** 第{round_num}轮-2操作_发生错误 |-> 文件读取失败")
                        continue
                    if len(file_content_list) == 0:
                        print(f" *** 第{round_num}轮-2操作_发生错误 |-> 文件内容为空")
                        continue

                    # 将解析后的所有元素添加到结果列表中
                    result_list.extend(file_content_list)
                    print(f" *** 第{round_num}轮-2操作_成功 |-> 数据已添加")

                except Exception as e:
                    print(f" *** 第{round_num}轮-2操作_发生错误 |-> {e} ")
                    continue

            elif user_choice == 3:
                # 调用文件选择对话框
                try:
                    print("*** 第{}轮-调用文件选择对话框 ***".format(round_num))

                    # 调用Windows_File_select函数处理文件选择
                    selected_files = Windows_File_select()

                    # 检查文件选择是否成功
                    if selected_files is None:
                        print(f" *** 第{round_num}轮-3操作_发生错误 |-> 文件选择失败")
                        continue
                    if len(selected_files) == 0:
                        print(f" *** 第{round_num}轮-3操作_发生错误 |-> 未选择有效文件")
                        continue

                    # 调用File_Read函数处理文件读取
                    file_content_list = File_Read(file_paths=selected_files)

                    # 将解析后的所有元素添加到结果列表中
                    result_list.extend(file_content_list)

                    print(f" *** 第{round_num}轮-3操作_成功 |-> 已选择 {len(selected_files)} 个文件")

                except Exception as e:
                    print(f" *** 第{round_num}轮-3操作_发生错误 |-> {e} ")
                    continue

            else:
                # 输入无效选项
                print(f" *** 第{round_num}轮-无效选项 |-> 请输入1-4之间的数字")
                continue

            # 对结果列表进行去重操作
            original_length = len(result_list)
            result_list = list(dict.fromkeys(result_list))  # 保持原有顺序的去重方法
            deduplicated_count = original_length - len(result_list)
            if deduplicated_count > 0:
                print(f" *** 第{round_num}轮-去重操作_成功 |-> 共删除 {deduplicated_count} 个重复元素")

            # 每次操作完成后暂停，让用户看到结果
            input("\n按回车键继续...")

    except Exception as e:
        print(f" *** File_Read函数执行过程中发生未知错误 |-> {e} ")
        return []

# import pandas as
def scan_XLS_then_XLSX(target_path=None):
    ###
    print("### 开始转换 ###")

    try:
        # 步骤1：根据第一个参数（目标路径）判断路径是否存在
        if not target_path:
            # 如果没有提供目标路径，则使用当前脚本所在的目录
            target_path = os.getcwd()  # 获取当前工作目录

        if not os.path.exists(target_path):
            raise FileNotFoundError(f"指定的目标路径 '{target_path}' 不存在")  # 如果路径不存在，抛出异常

        # 步骤2：使用os.walk方法扫描该路径目录下所有的Excel文件，并打印扫描结果
        # xls = 0
        xlsx = 0

        # 打印扫描结果
        print(f"# 实际扫描的文件夹路径: {target_path}")

        excel_files = []
        # xlsx_files = []
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.xls'):
                    excel_files.append(os.path.join(root, file))  # 收集所有 .xls 文件的完整路径
                    print(file)
                elif file.endswith('.xlsx'):
                    # xlsx_files.append(os.path.join(root, file))  # 收集所有 .xlsx 文件的完整路径
                    xlsx += 1  # 记录数量
                    print(file)

        xls = len(excel_files)
        print(f"# Excel (.xls) 文件数量: {xls}")
        # for file in excel_files:
        #     print(file)  # 每个 .xls 文件名称用一行单独显示

        # xlsx = len(xlsx_files)
        print(f"# Excel (.xlsx) 文件数量: {xlsx}")
        # for file in xlsx_files:
        #     print(file)  # 每个 .xlsx 文件名称用一行单独显示

        print(f"# excel文件总数量: { xls + xlsx}")

        # 初始化操作计数器
        num_operations = 0
        success_count = 0
        failed_count = 0

        # 步骤3：如果有需要转换格式的Excel文件，对文件逐个进行转换

        # 方法一 |--------------------------------------------------------------------------
        # for source_file in excel_files:
        #     base_name = os.path.splitext(os.path.basename(source_file))[0]  # 获取文件名去掉扩展名
        #     destination_file = os.path.join(os.path.dirname(source_file), f"{base_name}.xlsx")  # 构建目标文件的完整路径
        #
        #     try:
        #         # 读取 .xls 文件
        #         df = pd.read_excel(source_file, engine='xlrd')
        #
        #         # 写入 .xlsx 文件
        #         df.to_excel(destination_file, index=False, engine='openpyxl')
        #
        #         # 打印成功消息
        #         print(f"转换结果: 成功, 源文件: {source_file}, 输出文件: {destination_file}")
        #         success_count += 1  # 增加成功计数
        #     except Exception as e:
        #         # 打印失败原因
        #         print(f"转换结果: 失败, 源文件: {source_file}, 错误原因: {e}")
        #         failed_count += 1  # 增加失败计数
        #
        #     num_operations += 1  # 增加操作计数

        # 方法二 |--------------------------------------------------------------------------
        # excel = Dispatch("Excel.Application")
        #
        # for source_file in excel_files:
        #     base_name = os.path.splitext(os.path.basename(source_file))[0]  # 获取文件名去掉扩展名
        #     destination_file = os.path.join(os.path.dirname(source_file), f"{base_name}.xlsx")  # 构建目标文件的完整路径
        #
        #     try:
        #         # 读取 .xls 文件
        #         workbook = excel.Workbooks.Open(source_file)
        #
        #         # 写入 .xlsx 文件
        #         workbook.SaveAs(destination_file, FileFormat=51)
        #         workbook.Close()
        #
        #         # 打印成功消息
        #         print(f"转换结果: 成功, 源文件: {source_file}, 输出文件: {destination_file}")
        #         success_count += 1  # 增加成功计数
        #     except Exception as e:
        #         # 打印失败原因
        #         print(f"转换结果: 失败, 源文件: {source_file}, 错误原因: {e}")
        #         failed_count += 1  # 增加失败计数
        #
        #     num_operations += 1  # 增加操作计数
        #
        #     excel.Quit()

        # 方法二：改进 |--------------------------------------------------------------------------
        # 使用新创建的XLS_to_XLSX函数替换原有转换代码
        for source_file in excel_files:
            try:
                # 调用XLS_to_XLSX函数进行文件转换
                result = XLS_to_XLSX(source_file)

                # 根据转换结果更新计数器
                if result:
                    success_count += 1  # 转换成功，增加成功计数
                else:
                    failed_count += 1  # 转换失败，增加失败计数
                    num_operations += 1  # 增加操作计数

            except Exception as e:
                # 打印失败原因
                print(f"转换结果: 失败, 源文件: {source_file}, 错误原因: {e}")
                failed_count += 1  # 增加失败计数
                num_operations += 1  # 增加操作计数

        # 步骤4：输出字典显示操作总体情况
        print("### 转换结束 ###")
        result_dict = {
            "num": num_operations,
            "Success": success_count,
            "Failed": failed_count
        }
        return result_dict

    except Exception as e:
        # 如果函数异常中断，返回 None
        print(f"函数执行过程中发生错误: {e}")
        return None

# import os
# import pandas as pd

def xlsx_n_to_1(target_path=None, result_file_path=None):
    ###
    print("\n### 开始合并 ###")

    try:
        # 步骤1：根据两个参数分别判断路径是否存在，如果不存在先尝试创建
        if not target_path:
            target_path = os.getcwd()  # 获取当前工作目录

        if not os.path.exists(target_path):
            try:
                os.makedirs(target_path)
                print(f"*** 已创建路径-{target_path}")
            except Exception as e:
                print("***路径错误***")
                raise FileNotFoundError(f"无法创建目标路径 '{target_path}': {e}")
        else:
            print(f"***存在路径-{target_path}")

        if not result_file_path:
            result_file_path = os.getcwd()  # 获取当前工作目录

        if not os.path.exists(result_file_path):
            try:
                os.makedirs(result_file_path)
                print(f"*** 已创建路径-{result_file_path}")
            except Exception as e:
                print("***路径错误***")
                raise FileNotFoundError(f"无法创建结果文件路径 '{result_file_path}': {e}")
        else:
            print(f"***存在路径-{result_file_path}")

        # 存储目标操作路径和结果文件输出路径
        target_path = target_path
        result_file_path = result_file_path

        # 步骤2：扫描该路径目录下所有.xlsx后缀格式的Excel文件，并打印扫描结果
        
        excel_files = []
        
        # 定义需要跳过的文件夹名称列表，可以根据需要修改这个列表
        skip_folders = Exclude_Folder_OR_files  # 这里定义需要跳过的文件夹名称
        
        for root, dirs, files in os.walk(target_path):
            # 检查当前路径是否包含需要跳过的文件夹
            path_parts = root.split(os.sep)
            if any(skip_folder in path_parts for skip_folder in skip_folders):
                continue
                
            for file in files:
                if file.endswith('.xlsx'):
                    excel_files.append(os.path.join(root, file))  # 收集所有 .xlsx 文件的完整路径

        # 打印文件夹路径
        print(f"\n# 操作路径：{target_path}")

        # 打印扫描结果
        print(f"\nExcel (.xlsx) 文件数量: {len(excel_files)}")
        for file in excel_files:
            print(f"· {file}")  # 每个 .xlsx 文件名称用一行单独显示

        # 初始化操作计数器
        num_operations = 0
        success_count = 0
        failed_count = 0

        # 创建一个空的 DataFrame 来存储合并后的数据
        merged_df = pd.DataFrame()

        # 步骤3：如果有需要合并的Excel文件，则按字母顺序逐个读取excel文件内容
        for source_file in sorted(excel_files):
            try:
                # 读取Excel文件中的所有数据表
                xls = pd.ExcelFile(source_file)

                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)

                    # 根据表头合并数据，使用axis=0按行合并
                    merged_df = pd.concat([merged_df, df], axis=0, ignore_index=True, sort=False)

                    # 打印成功消息
                    print(f"···数据表读取合并成功:  {sheet_name}")

                success_count += 1  # 增加成功计数

            except Exception as e:
                # 打印失败原因
                print(f"## 读取合并失败: 源文件: {source_file}, 错误原因: {e}")
                failed_count += 1  # 增加失败计数

            num_operations += 1  # 增加操作计数

        # 在所有文件合并完成后再去除重复的行
        if not merged_df.empty:
            original_rows = len(merged_df)
            merged_df.drop_duplicates(inplace=True)
            final_rows = len(merged_df)
            print(f"## 去除重复行: {original_rows - final_rows} 行重复数据被删除")

        # 保存合并后的数据到结果文件
        result_file_full_path = os.path.join(result_file_path, "merged_output.xlsx")
        merged_df.to_excel(result_file_full_path, index=False, engine='openpyxl')
        print(f"## 文件已保存: {result_file_full_path}")

        # 步骤4：输出字典显示操作总体情况
        print("### 合并结束 ###")
        result_dict = {
            "num": num_operations,
            "Success": success_count,
            "Failed": failed_count
        }
        return result_dict

    except Exception as e:
        # 如果函数异常中断，返回 None
        print(f"### 函数执行过程中发生错误: {e}")
        return None

# import os
# import pandas as pd

def xlsx_rm_dup(source_file_path, sheet_names=None, condition_headers=None, target_file_path=None, target_sheet_name=None):
    """
    从指定的Excel文件中读取数据，并根据指定条件进行去重。
    
    参数:
    source_file_path (str): 源Excel文件路径
    sheet_names (list): 数据表名称列表，默认为所有数据表
    condition_headers (list): 条件表头列表，默认为所有表头
    target_file_path (str): 目标Excel文件路径，默认与源文件相同
    target_sheet_name (str): 目标数据表名称，默认与源数据表相同
    
    返回:
    dict: 统计结果字典，包括遍历总行数和删除的行数，异常中断则返回None
    """

    print("### 去重 ###")

    try:
        # 判断源文件是否存在
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"*** 文件不存在 - {source_file_path}")
        print(f"*** 存在路径 - {source_file_path}")

        # 获取源文件中的所有sheet名称
        all_sheets = pd.ExcelFile(source_file_path).sheet_names
        
        # 如果sheet_names为空，则默认为所有sheet
        if sheet_names is None or len(sheet_names) == 0:
            sheet_names = all_sheets
        else:
            # 检查指定的sheet是否存在于文件中
            for sheet in sheet_names:
                if sheet not in all_sheets:
                    raise ValueError(f"*** 数据表不存在 - {sheet}")
            print(f"*** 存在数据表 - {', '.join(sheet_names)}")

        # 设置目标文件路径和sheet名称
        if target_file_path is None or len(target_file_path.strip()) == 0:
            target_file_path = source_file_path
        else:
            # 尝试创建目标文件所在目录（如果不存在）
            target_dir = os.path.dirname(target_file_path)
            if not os.path.exists(target_dir) and len(target_dir.strip()) > 0:
                os.makedirs(target_dir)
                print(f"*** 已创建路径 - {target_dir}")
            elif os.path.exists(target_dir):
                print(f"*** 存在路径 - {target_dir}")
        
        if target_sheet_name is None or len(target_sheet_name.strip()) == 0:
            target_sheet_name = sheet_names[0]

        total_rows = 0
        removed_rows = 0

        with pd.ExcelWriter(target_file_path, mode='a' if os.path.exists(target_file_path) else 'w') as writer:
            for sheet in sheet_names:
                # 读取数据表内容
                df = pd.read_excel(source_file_path, sheet_name=sheet)
                
                initial_row_count = df.shape[0]
                total_rows += initial_row_count
                
                # 确定条件列，默认为所有列
                if condition_headers is None or len(condition_headers) == 0:
                    condition_columns = df.columns.tolist()
                else:
                    condition_columns = [col for col in condition_headers if col in df.columns]
                    if len(condition_columns) != len(condition_headers):
                        missing_cols = set(condition_headers) - set(df.columns)
                        raise ValueError(f"*** 表头不存在 - {missing_cols} 在数据表 {sheet}")
                
                # 去重操作
                original_df = df.copy()
                df.drop_duplicates(subset=condition_columns, keep='first', inplace=True)
                rows_removed = initial_row_count - df.shape[0]
                removed_rows += rows_removed
                
                # 打印被删除的行信息
                if rows_removed > 0:
                    duplicates = original_df.merge(df, on=condition_columns, how='outer', indicator=True)
                    duplicate_rows = duplicates[duplicates['_merge'] == 'left_only']
                    for _, row in duplicate_rows.iterrows():
                        dup_info = ', '.join([f"{header}-{row[header]}" for header in condition_columns])
                        print(f"· 数据表{sheet} - {dup_info} 重复->删除")
                
                # 写入去重后的数据到新的Excel文件
                df.to_excel(writer, sheet_name=target_sheet_name if sheet == sheet_names[0] else f"{target_sheet_name}_{sheet}", index=False)
                print(f"-> 已保存至 {target_file_path} - {target_sheet_name if sheet == sheet_names[0] else f'{target_sheet_name}_{sheet}'}")
            
        return {
            "total_rows": total_rows,
            "removed_rows": removed_rows
        }
    
    except Exception as e:
        print(f"发生错误: {e}")
        return None

# def xlsx_rm_dup(source_file_path, sheet_names=None, condition_headers=None, target_file_path=None, target_sheet_name=None):
#     """
#     从指定的Excel文件中读取数据，并根据指定条件进行去重。
    
#     参数:
#     source_file_path (str): 源Excel文件路径
#     sheet_names (list): 数据表名称列表，默认为所有数据表
#     condition_headers (list): 条件表头列表，默认为所有表头
#     target_file_path (str): 目标Excel文件路径，默认与源文件相同
#     target_sheet_name (str): 目标数据表名称，默认与源数据表相同
    
#     返回:
#     dict: 统计结果字典，包括遍历总行数和删除的行数，异常中断则返回None
#     """
#     try:
#         # 判断源文件是否存在
#         if not os.path.exists(source_file_path):
#             raise FileNotFoundError(f"*** 文件不存在 - {source_file_path}")
#         print(f"*** 存在路径 - {source_file_path}")

#         # 获取源文件中的所有sheet名称
#         all_sheets = pd.ExcelFile(source_file_path).sheet_names
        
#         # 如果sheet_names为空，则默认为所有sheet
#         if sheet_names is None or len(sheet_names) == 0:
#             sheet_names = all_sheets
#         else:
#             # 检查指定的sheet是否存在于文件中
#             for sheet in sheet_names:
#                 if sheet not in all_sheets:
#                     raise ValueError(f"*** 数据表不存在 - {sheet}")
#             print(f"*** 存在数据表 - {', '.join(sheet_names)}")

#         # 设置目标文件路径和sheet名称
#         if target_file_path is None or len(target_file_path.strip()) == 0:
#             target_file_path = source_file_path
#         else:
#             # 尝试创建目标文件所在目录（如果不存在）
#             target_dir = os.path.dirname(target_file_path)
#             if not os.path.exists(target_dir) and len(target_dir.strip()) > 0:
#                 os.makedirs(target_dir)
#                 print(f"*** 已创建路径 - {target_dir}")
#             elif os.path.exists(target_dir):
#                 print(f"*** 存在路径 - {target_dir}")
        
#         # 判断是否需要覆盖原文件
#         overwrite_original = (target_file_path == source_file_path and 
#                              (target_sheet_name is None or len(target_sheet_name.strip()) == 0))

#         if target_sheet_name is None or len(target_sheet_name.strip()) == 0:
#             # 当target_sheet_name为空时，使用原工作表名称列表
#             target_sheet_names = sheet_names
#         else:
#             # 当target_sheet_name不为空时，为每个工作表生成目标名称
#             target_sheet_names = [target_sheet_name if sheet == sheet_names[0] else f"{target_sheet_name}_{sheet}" 
#                                 for sheet in sheet_names]

#         total_rows = 0
#         removed_rows = 0

#         # 根据是否覆盖原文件选择不同的处理方式
#         if overwrite_original:
#             # 覆盖原文件的情况
#             with pd.ExcelWriter(target_file_path, mode='w', engine='openpyxl') as writer:
#                 for i, sheet in enumerate(sheet_names):
#                     # 读取数据表内容
#                     df = pd.read_excel(source_file_path, sheet_name=sheet)
                    
#                     initial_row_count = df.shape[0]
#                     total_rows += initial_row_count
                    
#                     # 确定条件列，默认为所有列
#                     if condition_headers is None or len(condition_headers) == 0:
#                         condition_columns = df.columns.tolist()
#                     else:
#                         condition_columns = [col for col in condition_headers if col in df.columns]
#                         if len(condition_columns) != len(condition_headers):
#                             missing_cols = set(condition_headers) - set(df.columns)
#                             raise ValueError(f"*** 表头不存在 - {missing_cols} 在数据表 {sheet}")
                    
#                     # 去重操作
#                     original_df = df.copy()
#                     df.drop_duplicates(subset=condition_columns, keep='first', inplace=True)
#                     rows_removed = initial_row_count - df.shape[0]
#                     removed_rows += rows_removed
                    
#                     # 打印被删除的行信息
#                     if rows_removed > 0:
#                         duplicates = original_df.merge(df, on=condition_columns, how='outer', indicator=True)
#                         duplicate_rows = duplicates[duplicates['_merge'] == 'left_only']
#                         for _, row in duplicate_rows.iterrows():
#                             dup_info = ', '.join([f"{header}-{row[header]}" for header in condition_columns])
#                             print(f"· 数据表{sheet} - {dup_info} 重复->删除")
                    
#                     # 写入去重后的数据到Excel文件
#                     df.to_excel(writer, sheet_name=target_sheet_names[i], index=False)
#                     print(f"-> 已保存至 {target_file_path} - {target_sheet_names[i]}")
#         else:
#             # 不覆盖原文件或写入不同文件的情况
#             with pd.ExcelWriter(target_file_path, mode='a' if os.path.exists(target_file_path) else 'w', 
#                                engine='openpyxl', if_sheet_exists='replace') as writer:
#                 for i, sheet in enumerate(sheet_names):
#                     # 读取数据表内容
#                     df = pd.read_excel(source_file_path, sheet_name=sheet)
                    
#                     initial_row_count = df.shape[0]
#                     total_rows += initial_row_count
                    
#                     # 确定条件列，默认为所有列
#                     if condition_headers is None or len(condition_headers) == 0:
#                         condition_columns = df.columns.tolist()
#                     else:
#                         condition_columns = [col for col in condition_headers if col in df.columns]
#                         if len(condition_columns) != len(condition_headers):
#                             missing_cols = set(condition_headers) - set(df.columns)
#                             raise ValueError(f"*** 表头不存在 - {missing_cols} 在数据表 {sheet}")
                    
#                     # 去重操作
#                     original_df = df.copy()
#                     df.drop_duplicates(subset=condition_columns, keep='first', inplace=True)
#                     rows_removed = initial_row_count - df.shape[0]
#                     removed_rows += rows_removed
                    
#                     # 打印被删除的行信息
#                     if rows_removed > 0:
#                         duplicates = original_df.merge(df, on=condition_columns, how='outer', indicator=True)
#                         duplicate_rows = duplicates[duplicates['_merge'] == 'left_only']
#                         for _, row in duplicate_rows.iterrows():
#                             dup_info = ', '.join([f"{header}-{row[header]}" for header in condition_columns])
#                             print(f"· 数据表{sheet} - {dup_info} 重复->删除")
                    
#                     # 写入去重后的数据到Excel文件
#                     df.to_excel(writer, sheet_name=target_sheet_names[i], index=False)
#                     print(f"-> 已保存至 {target_file_path} - {target_sheet_names[i]}")
            
#         return {
#             "total_rows": total_rows,
#             "removed_rows": removed_rows
#         }
    
#     except Exception as e:
#         print(f"发生错误: {e}")
#         return None

# import os
# import pandas as pd

def xlsx_export_SingleCondition(source_file_path, source_sheet_names, condition_header, target_file_path, target_sheet_name, conditions):
    """
    从指定的Excel文件中提取符合条件的数据，并导出到另一个Excel文件中。

    参数:
    source_file_path (str): 操作excel源文件路径（即 所在路径+文件名），不能为空。同时支持相对路径和绝对路径的输入。
    source_sheet_names (list): 源数据表名称，类型为list列表，元素为字符串，任一元素代表一张数据表。若为空，则默认为第一个参数所指定文件中的所有数据表。
    condition_header (str): 作为判断条件的列表头名称，类型为字符串，不能为空。
    target_file_path (str): 目标导出excel文件路径（即 所在路径+文件名），类型为字符串，不能为空。同时支持相对路径和绝对路径的输入。
    target_sheet_name (str): 目标导出数据表名称，类型为字符串。若为空，则默认为"Sheet1"，若"Sheet1"内容不为空，则"Sheet2"，以此类推直到空白数据表"Sheet{n}"，不存在则创建该空白数据表。
    conditions (list or str): 判断条件，类型为list列表或者string字符串。若为空，则默认为无条件，即任何输入均为合法。

    返回:
    dict: 操作统计结果，包含num(总次数)、Success(成功次数)、Failed(失败次数)，异常中断则返回None
    """
    try:
        # 步骤1: 参数验证和路径检查
        # 检查源文件路径是否为空
        if not source_file_path or not isinstance(source_file_path, str):
            raise ValueError("源文件路径不能为空")

        # 检查源文件是否存在
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"*** 不存在路径-{source_file_path}")
        else:
            print(f"*** 存在路径-{source_file_path}")

        # 获取源文件中的所有工作表名称
        all_sheets = pd.ExcelFile(source_file_path).sheet_names

        # 如果未指定工作表，则使用所有工作表
        if not source_sheet_names:
            source_sheet_names = all_sheets
            print("*** 使用所有数据表")
        else:
            # 检查指定的工作表是否存在
            for sheet in source_sheet_names:
                if sheet not in all_sheets:
                    raise ValueError(f"*** 不存在数据表-{sheet}")
            print(f"*** 存在数据表-{', '.join(source_sheet_names)}")

        # 检查条件表头名称是否为空
        if not condition_header or not isinstance(condition_header, str):
            raise ValueError("条件表头名称不能为空")

        # 检查目标文件路径是否为空
        if not target_file_path or not isinstance(target_file_path, str):
            raise ValueError("目标文件路径不能为空")

        # 确保目标文件路径存在，如果不存在则尝试创建目录
        target_dir = os.path.dirname(target_file_path)
        if target_dir and not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                print(f"*** 已创建路径-{target_dir}")
            except Exception as e:
                raise Exception(f"无法创建目标文件路径: {target_dir}")
        elif target_dir and os.path.exists(target_dir):
            print(f"*** 存在路径-{target_dir}")

        # 处理目标工作表名称
        if not target_sheet_name or not isinstance(target_sheet_name, str):
            # 如果目标工作表名称为空，需要找到第一个可用的Sheet名称
            if os.path.exists(target_file_path):
                # 如果目标文件存在，读取其工作表名称
                try:
                    target_wb = load_workbook(target_file_path)
                    target_sheet_name = "Sheet1"
                    i = 1
                    while target_sheet_name in target_wb.sheetnames:
                        if target_wb[target_sheet_name].max_row <= 1 and target_wb[target_sheet_name].max_column <= 1:
                            # 如果工作表几乎为空，则使用该工作表
                            break
                        i += 1
                        target_sheet_name = f"Sheet{i}"
                    target_wb.close()
                except Exception:
                    target_sheet_name = "Sheet1"
            else:
                target_sheet_name = "Sheet1"
        print(f"*** 将创建/使用数据表-{target_sheet_name}")

        # 初始化统计信息
        stats = {'num': 0, 'Success': 0, 'Failed': 0}

        # 获取源文件名（不含路径）
        source_filename = os.path.basename(source_file_path)

        # 步骤2: 循环读取每个工作表并进行条件判断
        for sheet_name in source_sheet_names:
            # 读取数据表内容
            df = pd.read_excel(source_file_path, sheet_name=sheet_name)

            # 检查条件列是否存在
            if condition_header not in df.columns:
                raise ValueError(f"*** 数据表{sheet_name} 中不存在列 {condition_header}")

            # 遍历每一行数据进行条件判断
            for index, row in df.iterrows():
                value = row[condition_header]
                # 判断条件是否满足
                # 如果conditions为空，则默认为无条件，即任何输入均为合法
                # 如果conditions为列表，则检查value是否在列表中
                # 如果conditions为字符串，则检查value是否等于该字符串
                is_valid = False
                if not conditions:
                    # 无条件，任何输入均为合法
                    is_valid = True
                elif isinstance(conditions, list) and value in conditions:
                    # conditions为列表且value在列表中
                    is_valid = True
                elif isinstance(conditions, str) and value == conditions:
                    # conditions为字符串且value等于conditions
                    is_valid = True

                # 根据判断结果输出信息
                if is_valid:
                    print(f"··· {source_filename}:{sheet_name}_第{index + 1}行 --- 合法")
                    stats['Success'] += 1
                else:
                    print(f"··· {source_filename}:{sheet_name}_第{index + 1}行 --- 非法")
                    stats['Failed'] += 1
                stats['num'] += 1

            # 步骤3: 将符合条件的数据追加到目标Excel文件
            # 筛选符合条件的数据
            if not conditions:
                # 无条件，所有行都符合条件
                filtered_df = df
            elif isinstance(conditions, list):
                # conditions为列表
                filtered_df = df[df[condition_header].isin(conditions)]
            else:
                # conditions为字符串
                filtered_df = df[df[condition_header] == conditions]

            if not filtered_df.empty:
                # 如果有符合条件的数据，写入目标文件
                if os.path.exists(target_file_path):
                    # 目标文件已存在
                    try:
                        # 加载目标工作簿
                        target_wb = load_workbook(target_file_path)
                        
                        # 检查目标工作表是否存在
                        if target_sheet_name in target_wb.sheetnames:
                            # 工作表存在，读取现有数据
                            target_ws = target_wb[target_sheet_name]
                            
                            # 获取现有表头
                            existing_headers = [cell.value for cell in target_ws[1] if cell.value is not None]
                            
                            # 确定列映射
                            header_mapping = {}
                            for col_idx, header in enumerate(filtered_df.columns):
                                if header in existing_headers:
                                    # 找到现有表头对应列
                                    header_mapping[header] = existing_headers.index(header) + 1
                                else:
                                    # 新增表头，放在最右侧
                                    header_mapping[header] = len(existing_headers) + 1
                                    target_ws.cell(row=1, column=len(existing_headers) + 1, value=header)
                                    existing_headers.append(header)
                            
                            # 追加数据行
                            start_row = target_ws.max_row + 1
                            for _, row_data in filtered_df.iterrows():
                                for header, col_num in header_mapping.items():
                                    target_ws.cell(row=start_row, column=col_num, value=row_data[header])
                                start_row += 1
                        else:
                            # 工作表不存在，创建新工作表并写入数据
                            target_ws = target_wb.create_sheet(target_sheet_name)
                            for col_idx, header in enumerate(filtered_df.columns, 1):
                                target_ws.cell(row=1, column=col_idx, value=header)
                            for row_idx, (_, row_data) in enumerate(filtered_df.iterrows(), 2):
                                for col_idx, header in enumerate(filtered_df.columns, 1):
                                    target_ws.cell(row=row_idx, column=col_idx, value=row_data[header])
                        
                        # 保存工作簿
                        target_wb.save(target_file_path)
                        target_wb.close()
                        print(f"- {source_filename}:{sheet_name}_判断结果 -> 已保存至{target_file_path}:{target_sheet_name}")
                    except Exception as e:
                        print(f"写入文件时出错: {str(e)}")
                        target_wb.close() if 'target_wb' in locals() else None
                        raise
                else:
                    # 目标文件不存在，创建新文件
                    filtered_df.to_excel(target_file_path, sheet_name=target_sheet_name, index=False, engine='openpyxl')
                    print(f"- {source_filename}:{sheet_name}_判断结果 -> 已保存至{target_file_path}:{target_sheet_name}")

        # 步骤4: 返回操作统计结果
        return stats

    except Exception as e:
        print(f"函数执行过程中发生错误: {str(e)}")
        return None

# import os
# import pandas as pd

def xlsx_sum_Condition_0(source_file_path, source_sheet_names, condition_header, target_file_path, target_sheet_name):
    try:
        # 检查源文件路径是否存在
        if not os.path.exists(source_file_path):
            print(f"*** 路径-{source_file_path} 不存在")
            raise FileNotFoundError(f"源文件路径 {source_file_path} 不存在")

        # 获取源文件中的所有工作表名称
        all_sheets = pd.ExcelFile(source_file_path).sheet_names

        # 如果source_sheet_names为空，则默认为所有工作表
        if not source_sheet_names:
            source_sheet_names = all_sheets
            print("*** 使用源文件中所有数据表")
        else:
            # 检查指定的工作表是否存在
            for sheet in source_sheet_names:
                if sheet not in all_sheets:
                    print(f"*** 数据表-{sheet} 不存在")
                    raise ValueError(f"数据表 {sheet} 不存在")

        # 确定目标文件路径和工作表名称
        target_dir = os.path.dirname(target_file_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"*** 已创建路径-{target_dir}")
        else:
            print(f"*** 存在路径-{target_dir}")

        # 如果目标文件不存在，创建一个空的Excel文件
        if not os.path.exists(target_file_path):
            pd.DataFrame().to_excel(target_file_path, engine='openpyxl')
            print(f"*** 已创建空Excel文件-{target_file_path}")

        # 确定目标工作表名称
        if not target_sheet_name:
            target_sheet_name = "Sheet1"
            # 检查工作表是否已存在，如果存在则生成新的工作表名称
            try:
                i = 1
                while True:
                    if f"{target_sheet_name}{i}" in pd.ExcelFile(target_file_path).sheet_names:
                        i += 1
                    else:
                        target_sheet_name = f"{target_sheet_name}{i}"
                        break
            except:
                # 如果无法读取现有工作表，则使用默认名称
                target_sheet_name = "Sheet1"
        print(f"*** 目标数据表-{target_sheet_name}")

        # 初始化统计结果字典
        stats_result = {}

        # 循环读取每个工作表并进行统计
        for sheet_name in source_sheet_names:
            df = pd.read_excel(source_file_path, sheet_name=sheet_name)

            # 检查条件列是否存在
            if condition_header not in df.columns:
                print(f"*** 数据表-{sheet_name} 中缺少条件表头-{condition_header}")
                continue

            # 统计每一行的数据
            for index, row in df.iterrows():
                condition_value = row[condition_header]
                parts = condition_value.split('\\')

                # 去掉前两个部分
                parts = parts[2:]

                # 找到第一个包含"供电局"的子字符串
                power_bureau_index = next((i for i, part in enumerate(parts) if '供电局' in part), None)
                if power_bureau_index is None:
                    continue

                primary_stat = parts[power_bureau_index].split('供电局')[0]
                secondary_stat = parts[power_bureau_index + 1] if power_bureau_index + 1 < len(parts) else None

                if primary_stat not in stats_result:
                    stats_result[primary_stat] = {}

                if secondary_stat not in stats_result[primary_stat]:
                    stats_result[primary_stat][secondary_stat] = 0

                stats_result[primary_stat][secondary_stat] += 1

                print(f"· 数据表-{sheet_name}-第{index+1}行 属于--{primary_stat}:{secondary_stat}")

        # 将嵌套字典格式化为三列表格（一级统计项、二级统计项、数量）
        formatted_data = []
        for primary_stat, secondary_dict in stats_result.items():
            for secondary_stat, count in secondary_dict.items():
                # 处理二级统计项为None的情况
                secondary = secondary_stat if secondary_stat is not None else ""
                formatted_data.append([primary_stat, secondary, count])

        # 创建包含三列的DataFrame：一级统计项、二级统计项、数量
        result_df = pd.DataFrame(formatted_data, columns=['Level-1', 'Level-2', 'num'])
        
        # 将统计数据保存到目标文件
        with pd.ExcelWriter(target_file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            # 如果工作表已存在，则先删除它
            if target_sheet_name in writer.book.sheetnames:
                std = writer.book[target_sheet_name]
                writer.book.remove(std)
            # 将数据写入指定的工作表
            result_df.to_excel(writer, sheet_name=target_sheet_name, index=False)

        print(f"-> 已保存至{target_file_path}-{target_sheet_name}")

        return stats_result

    except Exception as e:
        print(f"发生错误: {e}")
        return None

# import os
# import pandas as pd
# from openpyxl import load_workbook, Workbook

def count_dict_levels(d):
    """
    计算嵌套字典的最大层级数

    参数:
    d (dict): 需要计算层级数的嵌套字典

    返回:
    int: 字典的最大层级数
    """
    try:
        if not isinstance(d, dict):
            return 0
        if not d:
            return 1

        max_levels = 1
        for value in d.values():
            if isinstance(value, dict):
                levels = count_dict_levels(value)
                max_levels = max(max_levels, levels)
        return max_levels + 1
    except Exception as e:
        raise RuntimeError(f"计算字典层级数时发生错误: {str(e)}")

def match_and_fill(data_row, guide, depth, target_ws, source_filename, source_sheet_name, target_filename, target_sheet_name, row_index, stats):
    """
    递归匹配数据行和引导字典，并填写数据到目标单元格

    参数:
    data_row (list): 当前行的数据列表
    guide (dict): 引导字典
    depth (int): 当前递归深度
    target_ws: 目标工作表对象
    source_filename (str): 源文件名
    source_sheet_name (str): 源数据表名称
    target_filename (str): 目标文件名
    target_sheet_name (str): 目标数据表名称
    row_index (int): 当前行索引（从1开始）
    stats (dict): 操作统计字典

    返回:
    bool: 是否成功匹配并填写数据
    """
    try:
        # 如果到达最深层级，填写数据
        if not isinstance(guide, dict):
            try:
                # guide应该是目标单元格位置，如"A1"
                target_cell = guide
                # 数据行最右侧的值
                value_to_fill = data_row[-1] if data_row else ""

                # 填写数据到目标单元格
                target_ws[target_cell] = value_to_fill

                # 打印成功信息
                print(f"· {source_filename}:{source_sheet_name}_第{row_index}行-{{{value_to_fill}}} -> {target_filename}:{target_sheet_name}-[{target_cell}]")
                stats["Success"] += 1
                return True
            except Exception as e:
                print(f"· {source_filename}:{source_sheet_name}_第{row_index}行-{{{value_to_fill}}} -> 填写失败: {str(e)}")
                stats["Failed"] += 1
                return False

        # 如果还没到最深层级，继续匹配
        if depth < len(data_row):
            cell_value = str(data_row[depth]) if data_row[depth] is not None else ""

            # 遍历当前层级的键，查找匹配项
            for key, next_level in guide.items():
                key_str = str(key)
                # 检查键是否与当前单元格值匹配（严格匹配或子字符串）
                if key_str == cell_value or key_str in cell_value:
                    # 匹配成功，进入下一层级
                    return match_and_fill(data_row, next_level, depth + 1, target_ws, source_filename, source_sheet_name, target_filename, target_sheet_name, row_index, stats)

        # 没有找到匹配项
        if len(data_row) > 0:
            value_to_fill = data_row[-1] if data_row else ""
            print(f"· {source_filename}:{source_sheet_name}_第{row_index}行-{{{value_to_fill}}} -> 匹配失败")
        else:
            print(f"· {source_filename}:{source_sheet_name}_第{row_index}行- -> 匹配失败")
        stats["Failed"] += 1
        return False
    except Exception as e:
        raise RuntimeError(f"匹配和填写数据时发生错误: {str(e)}")

def xlsx_Fill_ExcelForm(source_file_path, source_sheet_name, guide_dict, target_file_path, target_sheet_name):
    """
    从指定Excel表中读取内容，根据json文件的预设参数，将读取的数据内容填到指定Excel表中的指定单元格

    参数:
    source_file_path (str): 操作excel源文件路径（即 所在路径+文件名），不能为空。同时支持相对路径和绝对路径的输入。
    source_sheet_name (str): 源数据表名称，不能为空。
    guide_dict (dict): 用于作为引导指示的嵌套字典，不能为空。
    target_file_path (str): 目标excel文件路径（即 所在路径+文件名），不能为空。同时支持相对路径和绝对路径的输入。
    target_sheet_name (str): 目标数据表名称，若为空，则默认为"Sheet1"，若"Sheet1"内容不为空，则"Sheet2"，以此类推直到空白数据表"Sheet{n}"，不存在则创建该空白数据表。

    返回:
    dict: 操作统计结果，包含num(总次数)、Success(成功次数)、Failed(失败次数)
    """
    try:
        # 步骤1: 参数验证和路径检查
        # 检查源文件路径
        if not source_file_path or not isinstance(source_file_path, str):
            raise ValueError("源文件路径不能为空")

        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"源文件不存在: {source_file_path}")
        print(f"*** 存在路径-{source_file_path}")

        # 检查源数据表名称
        if not source_sheet_name or not isinstance(source_sheet_name, str):
            raise ValueError("源数据表名称不能为空")

        # 检查引导字典
        if not guide_dict or not isinstance(guide_dict, dict):
            raise ValueError("引导字典不能为空")

        # 检查目标文件路径，如果不存在则尝试创建
        if not target_file_path or not isinstance(target_file_path, str):
            raise ValueError("目标文件路径不能为空")

        target_dir = os.path.dirname(target_file_path)
        if target_dir and not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                print(f"*** 已创建路径-{target_dir}")
            except Exception as e:
                raise Exception(f"无法创建目标文件路径: {target_dir}")
        elif target_dir and os.path.exists(target_dir):
            print(f"*** 存在路径-{target_dir}")

        # 如果目标文件不存在，创建一个空的Excel文件
        if not os.path.exists(target_file_path):
            wb = Workbook()
            wb.save(target_file_path)
            print(f"*** 已创建路径-{target_file_path}")
        else:
            print(f"*** 存在路径-{target_file_path}")

        # 检查源数据表是否存在
        source_sheets = pd.ExcelFile(source_file_path).sheet_names
        if source_sheet_name not in source_sheets:
            raise ValueError(f"源数据表 {source_sheet_name} 不存在")
        print(f"*** 存在数据表-{source_sheet_name}")

        # 处理目标数据表名称
        if not target_sheet_name or not isinstance(target_sheet_name, str):
            target_sheet_name = "Sheet1"

        # 步骤2: 读取源数据表内容并进行层级比较
        # 读取源数据表
        df_source = pd.read_excel(source_file_path, sheet_name=source_sheet_name)

        # 统计数据表层级数（列数）
        source_levels = len(df_source.columns)
        print(f"数据表层级数：{source_levels}")

        # 统计字典层级数
        dict_levels = count_dict_levels(guide_dict)
        print(f"字典层级数：{dict_levels}")

        # 比较层级数
        if source_levels == dict_levels:
            print("层级一致")
        else:
            raise ValueError(f"层级不一致：数据表层级数 {source_levels}，字典层级数 {dict_levels}")

        # 步骤3: 根据引导字典填写数据到目标Excel文件
        # 加载目标工作簿
        target_wb = load_workbook(target_file_path)

        # 检查目标工作表是否存在，如果不存在则创建
        if target_sheet_name not in target_wb.sheetnames:
            target_wb.create_sheet(target_sheet_name)
            print(f"*** 已创建数据表-{target_sheet_name}")
        else:
            print(f"*** 存在数据表-{target_sheet_name}")

        target_ws = target_wb[target_sheet_name]

        # 初始化操作统计
        stats = {
            "num": 0,
            "Success": 0,
            "Failed": 0
        }

        # 获取源文件名（不含路径）
        source_filename = os.path.basename(source_file_path)
        target_filename = os.path.basename(target_file_path)

        # 遍历源数据表的每一行
        for index, row in df_source.iterrows():
            stats["num"] += 1
            row_index = index + 1  # 行号从1开始

            # 将行数据转换为列表
            row_data = row.tolist()

            # 对当前行执行匹配和填写操作
            match_and_fill(row_data, guide_dict, 0, target_ws, source_filename, source_sheet_name, target_filename, target_sheet_name, row_index, stats)

        # 保存目标工作簿
        target_wb.save(target_file_path)

        # 步骤4: 返回操作统计结果
        return stats

    except Exception as e:
        print(f"函数执行过程中发生错误: {str(e)}")
        return None

### 排除项！！！
Exclude_Folder_OR_files = ['temp']

if __name__ == '__main__':
    print("------>>>>>>程序启动<<<<<<------\n")

    # 初始化
    print("######### 程序初始化检测 #########\n")

    # 初始化日志系统
    log_file = setup_logging()
    print(f"日志文件位置: {log_file}")

    ## 环境类型
    print("当前运行环境类型:", "打包环境\n" if check_if_bundled() else "开发环境\n")
    print("实际运行路径:", get_base_path())

    # 临时文件夹
    result = create_folder(folder_name="temp",
                           target_path=""
                           )
    print(result)
    print("")

    ## 参数配置
    try:
        config_path = get_resource_path("config/config.json")
        print("配置文件路径:", config_path)
        print("")

        xlsx_path = get_resource_path("config/第三方督查计划管控.xlsx")
        print("Excel文件路径:", xlsx_path)
        print("")

    except FileNotFoundError:
        print("配置文件不存在，但函数正常工作")
        print("\n！！！请检查配置文件或者输入后重启程序！！！\n")
        input("按任意按键退出程序········")
        exit()

    ## 模板准备
    FINAL = None
    try:
        FINAL = file_Move_OR_Copy( source_file_path=xlsx_path, target_path= "./temp", operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")

    #------------------------------------------------------------------------------------------------
    print("\n######### ！！！准备完毕，输入运行参数！！！ #########\n")

    plan = input("请输入需要填写的方案名称：\n")
    print("")

    config = Json_Check_Read( name=plan, json_path=config_path)
    if config:
        print("######### 当前校验结果为：TRUE ###########\n")
    else:
        print("\n！！！请检查配置文件或者输入后重启程序！！！\n")
        input("按任意按键退出程序········")
        exit()

    File_Sheet = input("请输入目标计划名称（一周报\双周报\三周报\月报\）：\n")

    Person_Name_list = RPA_OPcondition_Read()
    print( "\n再一次显示确认：\n", Person_Name_list)
    input("\n按任意按键继续········\n")

    # ------------------------------------------------------------------------------------------------

    result = scan_XLS_then_XLSX(target_path="")
    print(result)
    print("")

    result = xlsx_n_to_1( target_path="", result_file_path="./temp/")
    print(result)
    print("")

    result = xlsx_rm_dup( source_file_path="./temp/merged_output.xlsx", sheet_names=["Sheet1"], condition_headers=["作业计划编号"], target_file_path="./temp/RM_Duplicates.xlsx", target_sheet_name="Sheet1")
    print(result)
    print("")

    result = xlsx_export_SingleCondition( source_file_path="./temp/RM_Duplicates.xlsx", source_sheet_names=["Sheet1"], condition_header="姓名", target_file_path="./temp/ConditionExport.xlsx", target_sheet_name="Sheet1", conditions=Person_Name_list)
    print(result)
    print("")

    result = xlsx_sum_Condition_0( source_file_path="./temp/ConditionExport.xlsx", source_sheet_names=["Sheet1"], condition_header="所属业主项目部", target_file_path="./temp/ConditionSum.xlsx", target_sheet_name="Sheet1")
    print(result)

    result = xlsx_Fill_ExcelForm( source_file_path=r"./temp/ConditionSum.xlsx", source_sheet_name="Sheet1", guide_dict=config, target_file_path=r"./temp/第三方督查计划管控.xlsx", target_sheet_name=File_Sheet)
    print(result)
    print("")

    file_Move_OR_Copy( source_file_path=FINAL, target_path= "./", operation="copy")

    input("按任意按键退出程序········")
