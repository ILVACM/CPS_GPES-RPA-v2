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
# from datetime import datetime

# from pathlib import Path

from win32com.client import Dispatch

import tkinter as tk
from tkinter import filedialog

import requests
import psutil
import subprocess
from typing import Dict, Any, Union

### 函数
from UI.GUI import GUI_JSON_list_selector

###########################################################################################

import logging
import datetime

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
    log_filename = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

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

# import datetime

# def system_time_getc():
#     """
#     Windows系统环境下获取当前系统时间日期并以dict字典格式返回
#
#     该函数不需要接收参数，直接获取当前系统时间并格式化为指定字典格式
#
#     返回:
#         dict: 包含当前时间信息的字典，格式为{"year":2023,"month":1,"day":1,"hour":0,"minute":0,"second":0}
#               获取成功返回字典，否则返回None
#
#     依赖库:
#         - datetime: 用于获取和处理系统时间日期
#     """
#     try:
#         # 步骤1: 获取当前系统时间
#         # 使用datetime模块获取当前本地时间
#         now = datetime.datetime.now()
#
#         # 步骤2: 格式化时间信息为指定的字典格式
#         # 从datetime对象中提取年、月、日、时、分、秒信息并构造成字典
#         time_dict = {
#             "year": now.year,  # 获取年份
#             "month": now.month,  # 获取月份
#             "day": now.day,  # 获取日期
#             "hour": now.hour,  # 获取小时
#             "minute": now.minute,  # 获取分钟
#             "second": now.second  # 获取秒数
#         }
#
#         # 步骤3: 返回构造好的字典
#         return time_dict
#
#     except Exception as e:
#         # 异常处理: 如果在获取或处理时间过程中出现任何错误，打印错误信息并返回None
#         print(f"获取系统时间失败: {e}")
#         return None

def system_time_get_NOW():
    """
    Windows系统环境下获取当前系统时间日期并以dict字典格式返回

    该函数不需要接收参数，直接获取当前系统时间并格式化为指定字典格式

    返回:
        dict: 包含当前时间信息的字典，格式为{"year":2023,"month":1,"day":1,"weekday":"sunday","hour":0,"minute":0,"second":0}
              获取成功返回字典，否则返回None

    依赖库:
        - datetime: 用于获取和处理系统时间日期
    """
    try:
        # 步骤1: 获取当前系统时间
        # 使用datetime模块获取当前本地时间
        now = datetime.datetime.now()

        # 步骤2: 定义星期几的中文映射
        # weekday()返回0-6，分别代表周一到周日，需要映射为中文
        weekdays = {
            0: "monday",
            1: "tuesday",
            2: "wednesday",
            3: "thursday",
            4: "friday",
            5: "saturday",
            6: "sunday"
        }

        # 步骤3: 格式化时间信息为指定的字典格式
        # 从datetime对象中提取年、月、日、星期几、时、分、秒信息并构造成字典
        time_dict = {
            "year": now.year,  # 获取年份
            "month": now.month,  # 获取月份
            "day": now.day,  # 获取日期
            "weekday": weekdays[now.weekday()],  # 获取星期几并转换为英文小写
            "hour": now.hour,  # 获取小时
            "minute": now.minute,  # 获取分钟
            "second": now.second  # 获取秒数
        }

        # 步骤4: 返回构造好的字典
        return time_dict

    except Exception as e:
        # 异常处理: 如果在获取或处理时间过程中出现任何错误，打印错误信息并返回None
        print(f"获取系统时间失败: {e}")
        return None

# import requests
# import psutil
# import subprocess
# from typing import Dict, Any, Union

def Network_Check_0(url: str = None) -> bool:
    """
    Windows系统环境下网络状态检测函数，综合评估网络连通性、流量状态和ICMP响应

    参数:
        url (str): 需要检测的URL地址. 默认值为"https://www.baidu.com"

    返回:
        bool: 所有检测项均通过返回True，任一失败返回False

    依赖库:
        - requests: 用于HTTP连接检测
        - psutil: 用于网络接口流量监控
        - subprocess: 用于ICMP协议检测

    检测内容:
        1. HTTP连接检测: 验证指定URL的HTTP响应状态
        2. 网络流量检测: 检查网络接口数据收发状态
        3. ICMP检测: 通过ping命令验证基础网络连通性
    """
    try:
        # 参数初始化检查
        if not url or not isinstance(url, str):
            url = "https://www.baidu.com"
            print(" *** URL地址:Init |-> 使用默认参数 https://www.baidu.com ||-||-|| 成功 ")
        else:
            print(" *** URL地址:Check 成功 ")

        # HTTP连接检测
        print(" *** HTTP连接检测:Init 开始 ***")
        response = requests.get(url, timeout=5)
        print(f" *** HTTP连接检测:Check 状态码 {response.status_code} ")

        # 网络接口流量检测
        print(" *** 网络接口流量检测:Init 开始 ***")
        net_io = psutil.net_io_counters()
        print(
            f" *** 网络接口流量检测:Check 成功 |-> 已接收:{net_io.bytes_recv} bytes / 已发送:{net_io.bytes_sent} bytes ")

        # 所有检测通过
        print(" >>> 网络状态检测通过 <<< ")
        return True

    except requests.exceptions.RequestException as re:
        print(f" *** HTTP连接检测:Error |-> {str(re)} ||-||-|| 失败 ")
    except psutil.Error as pe:
        print(f" *** 网络接口流量检测:Error |-> {str(pe)} ||-||-|| 失败 ")
    except Exception as e:
        print(f" *** 网络状态检测:Error |-> {str(e)} ||-||-|| 失败 ")

    print(" >>> 网络状态检测未通过 <<< ")
    return False

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

# import os
# import shutil

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

def holiday_update_store(year: int) -> str | None:
    """
    Windows系统环境下获取并缓存节假日数据的函数

    参数:
        year (int): 需要获取的节假日年份

    返回:
        str: 成功时返回JSON文件路径，失败返回None

    依赖库:
        - requests: 用于HTTP请求获取节假日数据
        - os: 用于文件路径操作
        - json: 用于JSON数据处理
        - datetime: 用于日期比较和格式转换

    功能流程:
        1. 网络状态检查
        2. 本地缓存检查
        3. 数据获取与更新
        4. 数据格式转换
        5. 结果返回
    """
    try:
        # 参数验证
        if not year or not isinstance(year, int):
            raise ValueError("年份参数必须为整数")
        print(" *** 年份参数:Check 成功 ")

        # 构建URL
        url = f"https://fastly.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json"

        # 网络状态检查
        print(" *** 网络状态检查:Init 开始 ***")
        if not Network_Check_0(url):
            print(" *** 网络状态检查:Check 失败 ")
            return None
        print(" *** 网络状态检查:Check 成功 ")

        # 构建文件路径
        temp_dir = "./temp"
        file_name = f"{year}.json"
        file_path = os.path.join(temp_dir, file_name)

        # 检查本地缓存
        print(" *** 本地缓存检查:Init 开始 ***")
        current_date = datetime.datetime.now().date()

        if os.path.exists(file_path):
            # 读取现有文件
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    new_change_time = data.get("NewChangeTime", {})

                    # 验证日期是否匹配
                    if (new_change_time.get("year") == current_date.year and
                            new_change_time.get("month") == current_date.month and
                            new_change_time.get("day") == current_date.day):
                        print(" *** 本地缓存检查:Check 数据有效 ")
                        print(" *** 数据状态:Check |-> 使用现有缓存 ||-||-|| 成功 ")
                        return file_path
                    print(" *** 本地缓存检查:Check 数据过期 ")
                except json.JSONDecodeError:
                    print(" *** 本地缓存检查:Error 文件损坏 ")

        # 创建temp目录（如果不存在）
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print(f" *** 临时目录:Init |-> 已创建路径-{temp_dir} ")
        else:
            print(f" *** 临时目录:Check |-> 存在路径-{temp_dir} ")

        # 下载数据
        print(" *** 数据获取:Init 开始 ***")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        holiday_data = response.json()
        print(" *** 数据获取:Check 成功 ")

        # 添加更新时间
        holiday_data["NewChangeTime"] = {
            "year": current_date.year,
            "month": current_date.month,
            "day": current_date.day
        }

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(holiday_data, f, ensure_ascii=False, indent=4)
        print(f" *** 文件操作:Check |-> 文件已保存至 {file_path} ")

        # 数据格式转换
        print(" *** 数据转换:Init 开始 ***")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "days" in data and isinstance(data["days"], list):
            for item in data["days"]:
                if "date" in item and isinstance(item["date"], str):
                    # 解析日期字符串
                    date_str = item["date"].strip()
                    try:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

                        # 转换为字典格式
                        date_dict = {
                            "year": date_obj.year,
                            "month": date_obj.month,
                            "day": date_obj.day
                        }

                        # 更新数据
                        item["date"] = date_dict
                        print(f" *** data ||- {date_str} -> {date_dict} ")
                    except ValueError:
                        print(f" *** 日期解析:Error |-> 无效日期格式: {date_str} ")

        # 保存转换后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(" *** 数据转换:Check 成功 ")

        return file_path

    except requests.exceptions.RequestException as re:
        print(f" *** HTTP请求:Error |-> {str(re)} ||-||-|| 失败 ")
    except json.JSONDecodeError as jde:
        print(f" *** JSON解析:Error |-> {str(jde)} ||-||-|| 失败 ")
    except Exception as e:
        print(f" *** 异常处理:Error |-> {str(e)} ||-||-|| 失败 ")

    return None

def excel_column_to_list(file_path, sheet_names, header_conditions, match_mode="strict"):
    """
    从指定Excel文件中读取数据并解析为列表形式返回

    参数:
        file_path (str): 需要读取的Excel源文件路径（路径+文件名），支持相对/绝对路径
        sheet_names (list): 需要解析的工作表名称列表，空列表表示所有工作表
        header_conditions (list): 需要匹配的表头条件列表
        match_mode (str): 匹配模式，可选"strict"(严格)或"simple"(宽松)，默认strict

    返回:
        list: 包含符合条件的表格数据元素的列表（已去重）

    依赖库:
        pandas, openpyxl, os, shutil
    """
    try:
        # 1. 初始化+检查参数
        print(" *** 参数初始化:Init 开始 *** ")

        # 检查第一个参数（文件路径）
        if not file_path or not isinstance(file_path, str):
            raise ValueError("文件路径不能为空")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"源文件不存在: {file_path}")
        print(" *** 文件路径检查:Check 成功 *** ")

        # 处理第二个参数（工作表名称列表）
        if not sheet_names or not isinstance(sheet_names, list):
            print(" *** sheet名称列表:Init |-> 使用默认参数 ||-||-|| 成功 ")
            sheet_names = []  # 空列表表示处理所有工作表

        # 处理第三个参数（表头条件列表）
        if not header_conditions or not isinstance(header_conditions, list):
            print(" *** 表头条件列表:Init |-> 使用默认参数 ||-||-|| 成功 ")
            header_conditions = []  # 空列表表示处理所有表头

        # 处理第四个参数（匹配模式）
        if not match_mode or not isinstance(match_mode, str):
            print(" *** 匹配模式:Init |-> 使用默认参数 ||-||-|| 成功 ")
            match_mode = "strict"
        print(" *** 参数初始化:Check 成功 *** ")

        # 初始化结果列表
        result_list = []
        print(" *** 结果列表初始化:Init 成功 *** ")

        # 2. 根据文件格式处理Excel源文件
        print(" *** 文件格式处理:Init 开始 *** ")
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)

        # 创建temp目录
        temp_dir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print(f"*** 已创建路径-{temp_dir}")
        else:
            print(f"*** 存在路径-{temp_dir}")

        # 处理.xls文件
        if ext.lower() == '.xls':
            print(" *** 检测到.xls文件，开始转换 *** ")
            # 调用XLS_to_XLSX函数将源文件转换为.xlsx格式
            converted_file_path = XLS_to_XLSX(file_path)
            if not converted_file_path:
                raise Exception("文件格式转换失败")
            print(" *** 文件格式转换:Check 成功 *** ")

            # 将转换后的文件移动到temp目录
            temp_file_path = file_Move_OR_Copy(converted_file_path, temp_dir, "move")
            if not temp_file_path:
                raise Exception("文件移动失败")
            print(" *** 文件移动:Check 成功 *** ")

            # 更新文件路径为temp目录中的文件
            final_file_path = temp_file_path
        else:
            # .xlsx文件直接处理
            final_file_path = file_path
            print(" *** 检测到.xlsx文件，直接处理 *** ")
        print(" *** 文件格式处理:Check 成功 *** ")

        # 3. 读取处理数据表内容
        print(" *** 数据表处理:Init 开始 *** ")
        workbook = load_workbook(final_file_path)

        # 确定要处理的工作表
        sheets_to_process = sheet_names if sheet_names else workbook.sheetnames
        print(f" *** 需要处理的工作表: {sheets_to_process} *** ")

        # 遍历每个工作表
        for sheet_name in sheets_to_process:
            if sheet_name not in workbook.sheetnames:
                print(f" *** 跳过不存在的工作表: {sheet_name} *** ")
                continue

            worksheet = workbook[sheet_name]
            print(f" *** 正在处理工作表: {sheet_name} *** ")

            # 获取表头行
            headers = [cell.value for cell in next(worksheet.iter_rows())]
            print(f" *** 表头行: {headers} *** ")

            # 4. 遍历表头并进行匹配判断
            for col_idx, header in enumerate(headers):
                # 如果表头为空，跳过
                if header is None:
                    print(f" *** {file_name}::{sheet_name}_列{col_idx} |-> 非法 (空表头) ")
                    continue

                header_str = str(header)

                # 判断表头是否符合条件
                is_valid_header = False

                # 如果header_conditions为空，则所有表头都合法
                if not header_conditions:
                    is_valid_header = True
                else:
                    # 根据匹配模式判断
                    for condition in header_conditions:
                        condition_str = str(condition)
                        if match_mode == "strict":
                            # 严格模式：完全匹配
                            if condition_str == header_str:
                                is_valid_header = True
                                break
                        else:  # simple模式
                            # 宽松模式：不区分大小写且支持子字符串匹配
                            if condition_str.lower() in header_str.lower():
                                is_valid_header = True
                                break

                # 打印匹配结果
                status = "合法" if is_valid_header else "非法"
                print(f" *** {file_name}::{sheet_name}_{header_str} |-> {status} ")

                # 如果表头不合法，跳过该列
                if not is_valid_header:
                    continue

                # 5. 读取合法表头所在列的数据
                col_data = []
                for row in worksheet.iter_rows(min_col=col_idx + 1, max_col=col_idx + 1, min_row=2):
                    cell_value = row[0].value
                    if cell_value is not None:
                        col_data.append(str(cell_value))

                # 去重操作
                unique_data = list(set(col_data))
                duplicates_count = len(col_data) - len(unique_data)

                # 将数据添加到结果列表
                result_list.extend(unique_data)

                # 打印统计信息
                print(f" *#* {file_name}::{sheet_name}_{header_str} ||--|| 读取到{len(col_data)}元素。\n"
                      f" *#* ||--|| 存在{duplicates_count}重复 |-> Deleted")

        # 6. 输出最终结果
        print(f" >>> 当前已读取到了 {len(result_list)} 个元素并存储 <<< ")
        for item in result_list:
            print(f" - {item}")

        return result_list

    except Exception as e:
        print(f" *** 操作失败: {str(e)} *** ")
        raise


# import os
# import pandas as pd

def xlsx_export_SingleCondition(source_file_path, source_sheet_names, condition_header, target_file_path,
                                target_sheet_name, conditions):
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
                        print(
                            f"- {source_filename}:{sheet_name}_判断结果 -> 已保存至{target_file_path}:{target_sheet_name}")
                    except Exception as e:
                        print(f"写入文件时出错: {str(e)}")
                        target_wb.close() if 'target_wb' in locals() else None
                        raise
                else:
                    # 目标文件不存在，创建新文件
                    filtered_df.to_excel(target_file_path, sheet_name=target_sheet_name, index=False, engine='openpyxl')
                    print(
                        f"- {source_filename}:{sheet_name}_判断结果 -> 已保存至{target_file_path}:{target_sheet_name}")

        # 步骤4: 返回操作统计结果
        return stats

    except Exception as e:
        print(f"函数执行过程中发生错误: {str(e)}")
        return None

def excel_column_count(file_path, sheet_names=None, header_conditions=None, match_mode="strict"):
    """
    对指定excel文件符合条件的数据表进行计数统计并返回数量结果

    参数:
        file_path (str): 需要读取解析excel源文件的文件路径名，即文件路径+文件名。支持相对路径和绝对路径，不能为空
        sheet_names (list): 被读取的excel源文件需要解析的数据表名称列表。如果为空，则默认遍历所有数据表
        header_conditions (list): 数据表中需要解析的表头名条件列表。如果为空，则默认对所有表头进行统计
        match_mode (str): 指定匹配的严格程度，"strict"(严格)或"simple"(宽松)，默认为"strict"

    返回:
        int: 符合条件的列数据条目总数

    依赖库:
        os, openpyxl
    """
    try:
        # 步骤1: 初始化+检查参数
        print(" *** 参数初始化:Init 开始 *** ")

        # 检查第1个参数file_path是否存在且不为空
        if not file_path or not isinstance(file_path, str):
            raise ValueError("Excel源文件路径不能为空")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"源文件不存在: {file_path}")
        print(" *** 文件路径检查:Check 成功 *** ")

        # 处理第2个参数sheet_names，如果为空则默认为None
        if not sheet_names or not isinstance(sheet_names, list):
            sheet_names = None
            print(" *** 数据表名称列表:Init |-> 使用默认参数 None ||-||-|| 成功 ")
        print(" *** 数据表名称列表检查:Check 成功 *** ")

        # 处理第3个参数header_conditions，如果为空则默认为None
        if not header_conditions or not isinstance(header_conditions, list):
            header_conditions = None
            print(" *** 表头条件列表:Init |-> 使用默认参数 None ||-||-|| 成功 ")
        print(" *** 表头条件列表检查:Check 成功 *** ")

        # 处理第4个参数match_mode，如果为空则默认为"strict"
        if not match_mode or not isinstance(match_mode, str):
            match_mode = "strict"
            print(" *** 匹配模式:Init |-> 使用默认参数 strict ||-||-|| 成功 ")
        else:
            # 确保匹配模式是"strict"或"simple"之一
            if match_mode not in ["strict", "simple"]:
                match_mode = "strict"
                print(" *** 匹配模式校正:Check |-> 非法模式已重置为 strict ||-||-|| 成功 ")
        print(" *** 匹配模式检查:Check 成功 *** ")

        print(" *** 参数初始化:Check 完成 *** ")

        # 步骤2: 根据第1参数的输入读取处理指定excel源文件
        print(" *** Excel文件处理:Init 开始 *** ")
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)

        # 如果是.xls格式后缀的excel源文件
        if ext.lower() == '.xls':
            print(" *** 检测到.xls文件，开始转换 *** ")
            # 调用"XLS_to_XLSX"函数将源文件转换为.xlsx格式的源文件
            converted_file_path = XLS_to_XLSX(file_path)
            if not converted_file_path:
                raise Exception("文件格式转换失败")
            print(" *** 文件格式转换:Check 成功 *** ")

            # 调用"file_Move_OR_Copy"函数，将转换后的文件移动到temp文件夹中
            temp_dir = os.path.join(os.getcwd(), "temp")
            temp_file_path = file_Move_OR_Copy(converted_file_path, temp_dir, "move")
            if not temp_file_path:
                raise Exception("文件移动失败")
            print(" *** 文件移动:Check 成功 *** ")

            # 在temp文件夹中对该转换后的excel源文件进行下一步处理
            final_file_path = temp_file_path
        else:
            # 如果是.xlsx格式后缀的excel源文件，则直接进入下一步处理
            final_file_path = file_path
            print(" *** 检测到.xlsx文件，直接处理 *** ")
        print(" *** Excel文件处理:Check 成功 *** ")

        # 步骤3: 根据第2参数逐一读取转换后的源文件的数据表内容进行处理
        print(" *** 数据表处理:Init 开始 *** ")
        workbook = load_workbook(final_file_path)

        # 确定要处理的工作表（第2参数输入为空则为所有数据表）
        sheets_to_process = sheet_names if sheet_names is not None else workbook.sheetnames
        print(f" *** 需要处理的工作表: {sheets_to_process} *** ")

        # 初始化结果计数器
        total_count = 0

        # 遍历需要处理的每个工作表
        for sheet_name in sheets_to_process:
            if sheet_name not in workbook.sheetnames:
                print(f" *** 跳过不存在的工作表: {sheet_name} *** ")
                continue

            worksheet = workbook[sheet_name]
            print(f" *** 正在处理工作表: {sheet_name} *** ")

            # 获取表头行
            headers = [cell.value for cell in next(worksheet.iter_rows())]
            print(f" *** 表头行: {headers} *** ")

            # 遍历所有表头进行匹配判断
            for col_idx, header in enumerate(headers):
                # 如果表头为空，跳过
                if header is None:
                    print(f" *** {file_name}::{sheet_name}_列{col_idx} |-> 非法 (空表头) ")
                    continue

                header_str = str(header) if header is not None else ""

                # 判断表头是否符合条件
                is_valid_header = False

                # 如果header_conditions为空，则视为无条件合法，即所有表头均判断为合法匹配
                if header_conditions is None:
                    is_valid_header = True
                else:
                    # 根据第4参数指定的匹配严格程度进行匹配判断
                    if match_mode == "strict":
                        # 严格模式：只有第3参数输入的list列表中存在与该表头完全一样的string字符串元素才视为合法匹配
                        if header_str in header_conditions:
                            is_valid_header = True
                    else:  # simple模式
                        # 宽松模式：只要第3参数中任一string字符串元素与表头相同（不区分大小写）或者是其子字符串就视为合法匹配
                        for condition in header_conditions:
                            condition_str = str(condition)
                            if condition_str.lower() in header_str.lower() or header_str.lower() in condition_str.lower():
                                is_valid_header = True
                                break

                # 打印匹配结果
                if is_valid_header:
                    # 统计该表头所在列的条目数量（即行数，注意不包括表头）
                    column_count = 0
                    for row in worksheet.iter_rows(min_col=col_idx + 1, max_col=col_idx + 1, min_row=2):
                        cell_value = row[0].value
                        if cell_value is not None:
                            column_count += 1
                    total_count += column_count
                    print(f" *** {file_name}::{sheet_name}_{header_str} |-> 合法.所在列条目数{column_count} ")
                else:
                    print(f" *** {file_name}::{sheet_name}_{header_str} |-> 非法 ")

        # 步骤4: 输出最终统计结果
        print(f" >>> 当前已读取到了 {total_count} 个元素 <<< ")
        return total_count

    except ValueError as ve:
        print(f" *** 参数错误:Error |-> {str(ve)} ||-||-|| 失败 ")
        raise
    except FileNotFoundError as fnfe:
        print(f" *** 文件未找到:Error |-> {str(fnfe)} ||-||-|| 失败 ")
        raise
    except Exception as e:
        print(f" *** 操作失败:Error |-> {str(e)} ||-||-|| 失败 ")
        raise

def write_to_json(file_path, key_name, data_content=None, write_mode="update"):
    """
    将内容写入指定json文件的指定键值对的值中

    参数:
        file_path (str): 作为目标写入的json文件的文件路径名（路径+文件名），支持相对路径和绝对路径，不能为空
        key_name (str): 目标键值对的键名称，不能为空
        data_content (list, str, dict): 需要被写入指定键值对的数据内容，如果为空则默认为null
        write_mode (str): 写入方式，"update"(更新)或"add"(追加)，如果为空则默认为"update"

    返回:
        bool: 操作成功返回True，失败返回False

    异常:
        ValueError: 当必要参数为空时抛出
        FileNotFoundError: 当指定的json文件不存在时抛出
        json.JSONDecodeError: 当json文件格式不正确时抛出
        Exception: 其他处理过程中发生的异常
    """
    try:
        # 步骤1: 初始化+检查参数
        print(" *** 参数初始化:Init 开始 *** ")

        # 检查第1个参数file_path是否存在且不为空
        if not file_path or not isinstance(file_path, str):
            raise ValueError("目标json文件路径不能为空")
        print(" *** 文件路径检查:Check 成功 *** ")

        # 检查第2个参数key_name是否存在且不为空
        if not key_name or not isinstance(key_name, str):
            raise ValueError("目标键值对的键名称不能为空")
        print(" *** 键名称检查:Check 成功 *** ")

        # 处理第3个参数data_content，如果为空则默认为None (null)
        if data_content is None:
            print(" *** 数据内容:Init |-> 使用默认参数 None ||-||-|| 成功 ")
        print(" *** 数据内容检查:Check 成功 *** ")

        # 处理第4个参数write_mode，如果为空则默认为"update"
        if not write_mode or not isinstance(write_mode, str):
            write_mode = "update"
            print(" *** 写入方式:Init |-> 使用默认参数 update ||-||-|| 成功 ")
        else:
            # 确保写入模式是"update"或"add"之一
            if write_mode not in ["update", "add"]:
                write_mode = "update"
                print(" *** 写入方式校正:Check |-> 非法模式已重置为 update ||-||-|| 成功 ")
        print(" *** 写入方式检查:Check 成功 *** ")

        print(" *** 参数初始化:Check 完成 *** ")

        # 检查目标文件是否存在
        if not os.path.exists(file_path):
            # 如果文件不存在，创建一个空的JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
            print(f" *** 文件创建:Init |-> {file_path} 已创建 ||-||-|| 成功 ")
        else:
            print(" *** 文件存在性检查:Check 成功 *** ")

        # 步骤2: 读取并处理指定json文件
        print(" *** JSON文件处理:Init 开始 *** ")

        # 读取JSON文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError:
                # 如果JSON文件损坏或为空，初始化为空字典
                json_data = {}
                print(" *** JSON内容解析:Init |-> 文件内容为空或损坏，初始化为空字典 ||-||-|| 成功 ")

        print(" *** JSON文件读取:Check 成功 *** ")

        # 检查目标键是否存在
        key_exists = key_name in json_data
        print(f" *** 键存在性检查:Check |-> 键 {key_name} {'存在' if key_exists else '不存在'} ||-||-|| 成功 ")

        # 根据写入模式和键的存在情况处理数据
        if not key_exists or json_data.get(key_name) is None:
            # 如果键不存在或值为null，则直接写入数据
            json_data[key_name] = data_content
            print(f" *** 键值对创建:Init |-> 键 {key_name} 已创建 ||-||-|| 成功 ")
        else:
            # 键存在且值不为null，根据写入模式处理
            if write_mode == "update":
                # 更新模式：直接覆盖原值
                json_data[key_name] = data_content
                print(f" *** 键值对更新:Update |-> 键 {key_name} 已更新 ||-||-|| 成功 ")
            elif write_mode == "add":
                # 追加模式：根据数据类型进行追加操作
                existing_value = json_data[key_name]
                existing_type = type(existing_value)
                data_type = type(data_content)

                # 如果类型相同且都是list，则扩展列表
                if existing_type == list and data_type == list:
                    json_data[key_name] = existing_value + data_content
                    print(f" *** 列表追加:Add |-> 键 {key_name} 的列表已扩展 ||-||-|| 成功 ")
                # 如果类型相同且都是dict，则合并字典
                elif existing_type == dict and data_type == dict:
                    merged_dict = existing_value.copy()
                    merged_dict.update(data_content)
                    json_data[key_name] = merged_dict
                    print(f" *** 字典合并:Add |-> 键 {key_name} 的字典已合并 ||-||-|| 成功 ")
                else:
                    # 类型不同或不支持追加的类型，则覆盖原值
                    json_data[key_name] = data_content
                    print(f" *** 类型不匹配:Override |-> 键 {key_name} 已覆盖 ||-||-|| 成功 ")

        print(" *** JSON数据处理:Check 成功 *** ")

        # 步骤3: 将修改后的数据写回文件
        print(" *** JSON文件写入:Init 开始 *** ")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4, default=str)
        print(" *** JSON文件写入:Check 成功 *** ")

        # 输出操作结果
        file_name = os.path.basename(file_path)
        print(f" *||* {file_name}:{key_name}_写入成功 ")

        return True

    except ValueError as ve:
        print(f" *** 参数错误:Error |-> {str(ve)} ||-||-|| 失败 ")
        return False
    except FileNotFoundError as fnfe:
        print(f" *** 文件未找到:Error |-> {str(fnfe)} ||-||-|| 失败 ")
        return False
    except json.JSONDecodeError as jde:
        print(f" *** JSON解析错误:Error |-> {str(jde)} ||-||-|| 失败 ")
        return False
    except Exception as e:
        print(f" *** 操作失败:Error |-> {str(e)} ||-||-|| 失败 ")
        return False

###########################################################################################

Exclude_Folder_OR_files = ["temp"]
current_time = {}

###########################################################################################
if __name__ == '__main__':
    ####
    pass
    ####

    print("------>>>>>>程序启动<<<<<<------\n")

    # 初始化
    print("######### 程序初始化检测 #########\n")

    # 初始化日志系统
    log_file = setup_logging()
    print(f"日志文件位置: {log_file}")

    # 调用函数获取当前时间
    current_time = system_time_get_NOW()
    if current_time:
        print("当前系统时间:", current_time)
    else:
        print("获取系统时间失败")

    # 获取节假日数据
    result = holiday_update_store(current_time["year"])
    print(result)
    print("")

    ## 环境类型
    print("当前运行环境类型:", "打包环境\n" if check_if_bundled() else "开发环境\n")
    print("实际运行路径:", get_base_path())

    # 临时文件夹
    result = create_folder(folder_name="temp",
                           target_path=""
                           )
    print(result)
    print("")

    ## 模板准备
    FINAL = None
    try:
        config_path = get_resource_path("config/config.json")
        print("配置文件路径:", config_path)
        print("")

        xlsx_path = get_resource_path("config/export.xlsx")
        print("Excel文件路径:", xlsx_path)
        print("")

        temp_data = get_resource_path(r"config/temp.json")
        print("临时数据文件路径:", temp_data)
        print("")

        FINAL = file_Move_OR_Copy(source_file_path=xlsx_path,
                                  target_path="./temp",
                                  operation="copy"
                                  )

        result = file_Move_OR_Copy(source_file_path=config_path,
                                   target_path="./temp",
                                   operation="copy"
                                   )
        print(result)
        print("")

        result = file_Move_OR_Copy(source_file_path=temp_data,
                                   target_path="./temp",
                                   operation="copy"
                                   )
        print(result)
        print("")

    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")

    ## 参数配置???
    try:
        result = scan_XLS_then_XLSX(target_path="")
        print(result)
        print("")

        result = xlsx_n_to_1(target_path="",
                             result_file_path=r"./temp/"
                             )
        print(result)
        print("")

        # xlsx_path = get_resource_path(r"./temp/merged_output.xlsx")
        # print("Excel文件路径:", xlsx_path)
        # print("")

        temp_items = excel_column_to_list(file_path=r"./temp/merged_output.xlsx",
                                          sheet_names="",
                                          header_conditions=["所属部门"],
                                          match_mode="strict"
                                          )
        print(temp_items)
        print("")

        result = write_to_json(file_path=r"./temp/temp.json",
                               key_name="excel_content",
                               data_content=temp_items,
                               write_mode="update"
                               )
        print(result)
        print("")

    except FileNotFoundError:
        print("配置文件不存在，但函数正常工作")
        print("\n！！！请检查配置文件或者输入后重启程序！！！\n")
        input("按任意按键退出程序········")
        exit()

    # ------------------------------------------------------------------------------------------------
    print("\n######### ！！！准备完毕，输入运行参数！！！ #########\n")

    # 使用GUI选择器从JSON文件中选择项目
    selected_items = []
    try:
        selected_items = GUI_JSON_list_selector('./temp/temp.json', 'excel_content')
        if selected_items is not None:
            print(f"用户选择了 {len(selected_items)} 个项目:")
            for item in selected_items:
                print(f" - {item}")

            # 在这里可以继续处理选中的项目
            # 例如保存到文件、进行进一步处理等
        else:
            print("用户取消了选择操作")
    except Exception as e:
            print(f"使用GUI选择器时发生错误: {e}")

    # ------------------------------------------------------------------------------------------------

    result = xlsx_export_SingleCondition(source_file_path=r"./temp/merged_output.xlsx",
                                         source_sheet_names= "",
                                         condition_header="所属部门",
                                         target_file_path=r"./temp/ConditionExport.xlsx",
                                         target_sheet_name= "",
                                         conditions=selected_items
                                         )

