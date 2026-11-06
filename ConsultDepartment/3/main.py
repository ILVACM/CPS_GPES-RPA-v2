def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。
    
import os
import sys

import json

import requests
import psutil
import subprocess


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

        full_path = os.path.join(base_path, relative_path)

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


import logging
from datetime import datetime

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
        now = datetime.now()

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

def Time_dict_TO_string(time_dict, format_string):
    """
    将包含日期时间信息的字典转换为指定格式的字符串。

    参数:
    time_dict (dict): 包含日期时间信息的字典。
                      必须包含键 'year', 'month', 'day', 'hour', 'minute', 'second'。
    format_string (str): 用于格式化输出的 strftime 格式字符串。
                         如果为空字符串或 None，则默认使用 '%Y-%m-%d_%H:%M:%S'。

    返回:
    str: 格式化后的日期时间字符串。

    异常:
    ValueError: 如果 time_dict 为 None，或缺少必要的键，或键对应的值无效。
    TypeError: 如果 time_dict 不是字典类型。
    """
    try:
        # 步骤 1: 初始化和检查
        print(" *** 参数检查:Check 成功 ")

        # 检查第一个参数 time_dict 是否存在且不为 None
        if time_dict is None:
            raise ValueError("输入的 time_dict 不能为 None。")

        # 检查第一个参数 time_dict 是否为字典类型
        if not isinstance(time_dict, dict):
            raise TypeError("第一个参数 time_dict 必须是字典类型。")

        # 检查字典中是否包含所有必需的键
        required_keys = ['year', 'month', 'day', 'hour', 'minute', 'second']
        for key in required_keys:
            if key not in time_dict:
                raise ValueError(f"输入的字典中缺少必需的键: '{key}'。")

        print(" *** 必需键存在性检查:Check 成功 ")

        # 检查并初始化第二个参数 format_string
        if not format_string:
            format_string = '%Y-%m-%d_%H:%M:%S'
            print(" *** 格式字符串初始化:Init 成功 (使用默认格式 '%Y-%m-%d_%H:%M:%S') ")
        else:
            print(" *** 格式字符串检查:Check 成功 ")

        # 步骤 2: 提取字典中的值并创建 datetime 对象
        year = time_dict['year']
        month = time_dict['month']
        day = time_dict['day']
        hour = time_dict['hour']
        minute = time_dict['minute']
        second = time_dict['second']

        print(" *** 日期时间值提取:Extract 成功 ")

        # 使用提取的值创建 datetime 对象
        # datetime 构造函数会自动检查值的有效性（如 month=13 会抛出异常）
        dt_object = datetime(year, month, day, hour, minute, second)
        print(" *** datetime 对象创建:Create 成功 ")

        # 步骤 3: 使用 strftime 格式化 datetime 对象
        formatted_time_string = dt_object.strftime(format_string)
        print(" *** 日期时间格式化:Format 成功 ")

        # 返回格式化后的字符串
        return formatted_time_string

    except (ValueError, TypeError) as e:
        # 捕获 ValueError 和 TypeError 并重新抛出，提供更清晰的错误信息
        print(f" *** 错误:Error 发生 - {e} ")
        raise e
    except Exception as e:
        # 捕获其他未预期的异常
        print(f" *** 未预期错误:Unexpected Error 发生 - {e} ")
        raise e

# import os
import shutil


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


import os  # 用于文件路径操作和检查文件是否存在


def JSON_CleanUP(file_path: str) -> bool:
    """
    在Windows系统环境下，清空指定JSON文件的内容。

    该函数会打开指定路径的文件（如果文件不存在则创建一个空文件），
    并将其内容截断（清空）。

    Args:
        file_path (str): 需要清空内容的JSON文件的路径（相对路径或绝对路径）。
                         例如: "data/config.json", "C:\\Users\\User\\Documents\\settings.json"

    Returns:
        bool: 如果清空操作成功，则返回 True；如果发生错误，则返回 False。

    Raises:
        该函数内部处理所有异常，不会向调用者抛出异常。

    注意:
        - 此函数依赖于操作系统对文件的操作权限。
        - 虽然命名为JSON_CleanUP，但实际可以清空任何文本文件的内容。
    """
    try:
        # --- 参数验证 ---
        # 1. 检查输入的 file_path 是否为字符串类型
        if not isinstance(file_path, str):
            print(f"错误: 输入参数 'file_path' 必须是字符串类型，当前类型为 {type(file_path)}。")
            return False

        # 2. 检查输入的 file_path 是否为空字符串
        if not file_path.strip():  # strip() 用于去除字符串首尾的空白字符
            print("错误: 输入参数 'file_path' 不能为空字符串或仅包含空白字符。")
            return False

        # --- 路径处理 ---
        # 3. (可选) 规范化路径，处理路径中的 '.' 和 '..' 等符号
        # os.path.normpath 有助于处理不同操作系统下的路径分隔符差异，
        # 在Windows上也能很好地工作。
        normalized_path = os.path.normpath(file_path)
        # print(f"处理后的规范化路径: {normalized_path}") # 可用于调试

        # --- 文件操作 ---
        # 4. 使用 'w+' 模式打开文件。'w+' 模式的含义是：
        #    - 如果文件存在，打开它并截断（清空）其内容。
        #    - 如果文件不存在，创建一个新文件。
        #    - 文件指针位于文件开头。
        #    - 可以进行读写操作（虽然本例中我们只关心清空）。
        #    使用 'with' 语句确保文件在操作后能被正确关闭，即使发生异常也是如此。
        with open(normalized_path, 'w', encoding='utf-8') as f:
            # 5. 在 'w+' 模式下打开并立即关闭（或在with块结束时关闭）
            #    文件已经被截断（清空）了。这里显式地截断是为了更明确地表达意图，
            #    虽然在此模式下通常是不必要的。
            f.truncate(0)  # 将文件大小截断为0字节，确保内容被清空

        # --- 操作成功 ---
        # 6. 如果执行到这里没有抛出异常，说明清空操作成功。
        print(f"成功清空文件内容: {normalized_path}")
        return True

    except FileNotFoundError:
        # 7. 处理文件未找到的异常。理论上 'w+' 模式会创建文件，
        #    但如果路径中的目录不存在，则可能抛出此异常。
        print(f"错误: 找不到文件或路径 '{file_path}'。请检查路径是否正确以及父目录是否存在。")
        return False
    except PermissionError:
        # 8. 处理权限不足的异常，例如文件被其他程序占用或没有写入权限。
        print(f"错误: 没有权限清空文件 '{file_path}'。请检查文件是否被占用或用户是否有写入权限。")
        return False
    except OSError as e:
        # 9. 处理其他操作系统相关的错误，如路径名过长等。
        print(f"操作系统错误: 在处理文件 '{file_path}' 时发生错误: {e}")
        return False
    except Exception as e:
        # 10. 捕获所有其他未预期的异常，保证函数不会崩溃。
        print(f"发生未知错误: 在清空文件 '{file_path}' 时发生未预期的错误: {e}")
        return False


import os

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
                return ""  # 返回空字符串表示失败

    # 新文件夹的完整路径
    full_path = os.path.join(target_path, folder_name)  # 将目标路径和文件夹名称连接形成完整路径

    # 步骤3：在指定路径下创建文件夹
    try:
        os.mkdir(full_path)  # 尝试在指定路径下创建目录
        print(f"文件夹 '{folder_name}' 成功创建于 '{full_path}'")  # 打印成功消息
        return full_path  # 返回创建的文件夹完整路径
    except FileExistsError:
        print(f"文件夹 '{folder_name}' 已经存在于 '{full_path}'")  # 打印消息如果文件夹已经存在
        return ""  # 返回空字符串表示失败
    except PermissionError:
        print(f"权限被拒绝: 无法在 '{full_path}' 创建文件夹 '{folder_name}'")  # 打印消息如果权限被拒绝
        return ""  # 返回空字符串表示失败
    except Exception as e:
        print(f"创建文件夹 '{folder_name}' 时发生错误: {e}")  # 打印任何其他发生的异常
        return ""  # 返回空字符串表示失败

import os
from openpyxl import load_workbook

def excel_XLSX_Read_sheets(file_path: str) -> list:
    """
    读取指定 .xlsx Excel 文件中所有数据表（工作表）的名称。

    此函数会打开一个 .xlsx 文件，遍历其中的所有工作表，
    并将每个工作表的名称与文件名组成一个字典，存入列表后返回。

    Args:
        file_path (str):
            需要读取的 Excel 文件的路径（相对路径或绝对路径）。
            该路径不能为空。

    Returns:
        list[dict]:
            一个列表，其中每个元素都是一个字典。
            字典的键是 'file_name'，值是不带路径的Excel文件名；
            字典的键是 'sheet_name'，值是对应的工作表名称。
            例如: [{'file_name': 'data.xlsx', 'sheet_name': 'Sheet1'}, ...]

    Raises:
        ValueError: 如果输入的 file_path 为空。
        FileNotFoundError: 如果指定的文件路径不存在。
        Exception: 如果在读取文件或处理数据时发生其他错误。
    """
    # --- 步骤 1: 初始化和检查 ---
    try:
        # 检查参数是否为空
        if not file_path or not isinstance(file_path, str):
            print(f" *** 参数检查:Check 失败 - 输入的文件路径无效或为空")
            raise ValueError("文件路径不能为空或非字符串类型。")

        print(f" *** 参数检查:Check 成功 - 接收到文件路径: {file_path}")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f" *** 文件存在性检查:Check 失败 - 文件不存在: {file_path}")
            raise FileNotFoundError(f"指定的文件路径不存在: {file_path}")

        print(f" *** 文件存在性检查:Check 成功 - 文件存在: {file_path}")

        # 获取不带路径的文件名，用于构建键值对
        file_name = os.path.basename(file_path)
        print(f" *** 获取文件名:Init 成功 - 提取文件名: {file_name}")

        # 初始化结果列表
        result_list = []
        print(f" *** 结果列表初始化:Init 成功")

        # --- 步骤 2: 读取数据表名称 ---
        # 使用 openpyxl 加载工作簿（read_only=True 提高效率）
        workbook = load_workbook(filename=file_path, read_only=True)
        print(f" *** 加载工作簿:Check 成功 - 成功打开文件 {file_name}")

        # 遍历所有工作表的名称
        for sheet_name in workbook.sheetnames:
            # 构建键值对字典
            # sheet_info = {
            #    "file_name": file_name,
            #    "sheet_name": sheet_name
            # }
            sheet_info = {
                file_name: sheet_name
            }
            # 将字典添加到结果列表
            result_list.append(sheet_info)
            print(f" *** {file_name}::{sheet_name} ||-> ADD ")

        # 关闭工作簿
        workbook.close()
        print(f" *** 关闭工作簿:Check 成功 - 已关闭文件 {file_name}")

        # --- 步骤 3: 返回结果 ---
        print(f" *** 数据读取完成:Check 成功 - 共读取 {len(result_list)} 个工作表")
        return result_list

    except ValueError as ve:
        # 重新抛出由参数检查引发的 ValueError
        raise ve
    except FileNotFoundError as fnfe:
        # 重新抛出由文件不存在引发的 FileNotFoundError
        raise fnfe
    except Exception as e:
        # 捕获并处理其他所有异常
        print(f" *** 操作过程中发生未预期的错误:Error - {e}")
        raise e  # 重新抛出异常，让调用者知道发生了错误


import os

def excel_Scan_XLSX(directory_path: str = None, exclude_list: list = None) -> list:
    """
    扫描指定目录及其子目录下所有 .xlsx 格式的 Excel 文件，并返回文件名列表。
    支持通过排除列表忽略特定的文件或文件夹。

    此函数会递归遍历给定目录（或默认的当前脚本目录），
    查找所有以 .xlsx 结尾的文件。在遍历过程中，如果遇到的
    文件名或文件夹名包含在 exclude_list 中的任意一个字符串作为子串，
    则会跳过该文件或整个文件夹。
    最终将所有找到的 .xlsx 文件的文件名（不包含路径）添加到列表中返回。

    Args:
        directory_path (str, optional):
            需要扫描的目录路径（相对路径或绝对路径）。
            如果未提供或为空字符串，则默认使用当前脚本所在的目录。
        exclude_list (list, optional):
            一个包含需要排除的文件名或文件夹名关键词的列表。
            在扫描过程中，如果文件或文件夹名称包含列表中的任意一个字符串，
            将会被忽略。如果未提供或为空，则不进行任何排除，递归扫描所有内容。

    Returns:
        list[str]:
            一个列表，其中每个元素都是一个找到的 .xlsx 文件的文件名（不含路径）。
            例如: ['report1.xlsx', 'data.xlsx', ...]

    Raises:
        ValueError: 如果提供的 directory_path 不是目录或不存在。
        Exception: 如果在扫描目录或处理文件时发生其他未预期的错误。
    """
    # --- 步骤 1: 初始化和检查 ---
    try:
        # 检查并设置目录路径
        if not directory_path:
            # 获取当前执行脚本的绝对路径，然后获取其所在的目录
            directory_path = os.path.dirname(os.path.abspath(__file__))
            print(f" *** 参数为空，使用默认目录:Init 成功 - 设置为当前脚本目录: {directory_path}")
        else:
            print(f" *** 参数检查:Check 成功 - 接收到目录路径: {directory_path}")

        # 规范化路径，处理路径中的 .. 或 . 等
        directory_path = os.path.normpath(directory_path)

        # 检查路径是否存在
        if not os.path.exists(directory_path):
            print(f" *** 路径存在性检查:Check 失败 - 路径不存在: {directory_path}")
            raise ValueError(f"指定的目录路径不存在: {directory_path}")

        # 检查路径是否确实是一个目录
        if not os.path.isdir(directory_path):
            print(f" *** 目录有效性检查:Check 失败 - 路径不是目录: {directory_path}")
            raise ValueError(f"指定的路径不是一个目录: {directory_path}")

        print(f" *** 目录存在性及有效性检查:Check 成功 - 目录有效: {directory_path}")

        # 处理排除列表
        if not exclude_list or not isinstance(exclude_list, list):
            exclude_list = []
            print(f" *** 排除列表检查:Check 成功 - 未提供排除列表或列表为空，将扫描所有文件")
        else:
            # 确保排除列表中的元素是字符串，便于后续比较
            exclude_list = [item for item in exclude_list if isinstance(item, str)]
            print(f" *** 排除列表检查:Check 成功 - 使用排除列表: {exclude_list}")

        # 初始化结果列表
        result_list = []
        print(f" *** 结果列表初始化:Init 成功")

        # --- 步骤 2: 递归扫描目录并读取文件名 ---
        def _scan_recursively(current_path):
            """
            内部递归函数，用于实际执行扫描逻辑。
            :param current_path: 当前正在扫描的目录路径。
            """
            print(f" *** 开始扫描子目录:Check 成功 - 正在扫描: {current_path}")

            try:
                # os.scandir() 比 os.listdir() 更高效
                with os.scandir(current_path) as entries:
                    for entry in entries:
                        # 获取不带路径的名称用于比较和添加
                        entry_name = entry.name

                        # --- 检查是否需要排除 ---
                        # 检查entry_name是否包含exclude_list中的任意一个字符串
                        should_exclude = False
                        for exclude_item in exclude_list:
                            if exclude_item in entry_name:
                                should_exclude = True
                                break
                        
                        if should_exclude:
                            if entry.is_file():
                                print(f" *** 排除文件:Check 成功 - 跳过文件: {entry.path}")
                            elif entry.is_dir():
                                print(f" *** 排除目录:Check 成功 - 跳过整个目录: {entry.path}")
                            continue  # 跳过当前文件或目录

                        # --- 处理文件 ---
                        if entry.is_file():
                            # 检查文件名是否以 .xlsx 结尾（不区分大小写）
                            if entry_name.lower().endswith('.xlsx'):
                                result_list.append(entry_name)
                                print(f" *** {entry_name} ||-> ADD ")

                        # --- 处理目录并递归 ---
                        elif entry.is_dir():
                            # 如果是目录，则递归调用自身进行扫描
                            _scan_recursively(entry.path)

            except PermissionError as pe:
                # 如果没有权限访问某个子目录，记录日志并继续扫描其他部分
                print(f" *** 目录访问权限警告:Warning - 没有权限访问目录 '{current_path}': {pe}")
                # 这里选择不中断整个过程，只是跳过这个无法访问的目录

        # 启动递归扫描
        _scan_recursively(directory_path)

        # --- 步骤 3: 返回结果 ---
        print(f" *** 目录扫描完成:Check 成功 - 共找到 {len(result_list)} 个 .xlsx 文件")
        return result_list

    except ValueError as ve:
        # 重新抛出由参数或路径检查引发的 ValueError
        raise ve
    except Exception as e:
        # 捕获并处理其他所有异常
        print(f" *** 操作过程中发生未预期的错误:Error - {e}")
        raise e  # 重新抛出异常，让调用者知道发生了错误

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

        print(f"# excel文件总数量: {xls + xlsx}")

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


from win32com.client import Dispatch

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

import os
from openpyxl import load_workbook, Workbook

def excel_XLSX_Merge_Sheet(
        source_directory: str,
        source_sheet_list: list,
        target_file_path: str,
        target_sheet_name: str = None,
        sort_columns: list = None  # 新增参数，用于指定排序的列
) -> str:
    """
    将指定目录下多个Excel (.xlsx)文件中的指定工作表合并到一个新的工作表中，
    并保存到目标Excel文件中。

    Args:
        source_directory (str):
            包含源Excel文件的目录路径（相对或绝对）。如果为空，则使用脚本所在目录。
        source_sheet_list (list):
            包含需要合并的源文件和工作表信息的列表。
            列表中每个元素是一个字典，格式为 {'源文件名.xlsx': '源工作表名'}。
            此参数不能为空。
        target_file_path (str):
            目标Excel文件的完整路径（包含文件名）。如果文件不存在会被创建。
            此参数不能为空。
        target_sheet_name (str, optional):
            目标工作表的名称。如果为空或None，则会自动查找一个可用的 'Sheet{num}' 名称。
            如果指定名称的工作表已存在，其内容将被覆盖。
        sort_columns (list, optional):
            用于排序的列名列表。按照列表中列名的顺序，逐个列按字典序升序排序。
            如果为空或None，则不进行排序。

    Returns:
        str: 实际保存的目标文件的完整路径。

    Raises:
        ValueError: 如果必要参数为空、源列表格式错误或目录/文件路径无效。
        FileNotFoundError: 如果指定的源文件在目录中找不到。
        Exception: 如果在读取、写入或处理Excel文件时发生其他错误。
    """
    # --- 步骤 1: 初始化和检查 ---
    try:
        # 检查 source_sheet_list 参数
        if not source_sheet_list or not isinstance(source_sheet_list, list):
            print(f" *** 源列表参数检查:Check 失败 - source_sheet_list 不能为空且必须是列表")
            raise ValueError("source_sheet_list 不能为空且必须是列表。")

        # 检查并规范化 source_directory
        if not source_directory:
            source_directory = os.path.dirname(os.path.abspath(__file__))
            print(f" *** 源目录参数为空，使用默认目录:Init 成功 - 设置为: {source_directory}")
        else:
            source_directory = os.path.normpath(source_directory)
            print(f" *** 源目录参数检查:Check 成功 - 接收到目录路径: {source_directory}")

        if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
            print(f" *** 源目录存在性检查:Check 失败 - 路径不存在或不是目录: {source_directory}")
            raise ValueError(f"源目录路径无效: {source_directory}")
        print(f" *** 源目录存在性检查:Check 成功 - 目录有效: {source_directory}")

        # 检查 target_file_path 参数
        if not target_file_path:
            print(f" *** 目标文件路径检查:Check 失败 - target_file_path 不能为空")
            raise ValueError("target_file_path 不能为空。")
        target_file_path = os.path.normpath(target_file_path)
        target_dir = os.path.dirname(target_file_path)
        print(f" *** 目标文件路径检查:Check 成功 - 目标文件路径: {target_file_path}")

        # 确保目标文件的目录存在
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f" *** 目标目录创建:Init 成功 - 已创建目录: {target_dir}")

        # 处理 target_sheet_name
        if not target_sheet_name:
            target_sheet_name = "Sheet1"  # 默认名称，后续会检查是否需要更改
            print(f" *** 目标工作表名称为空，将初始化:Init 成功 - 初始名称: {target_sheet_name}")
        else:
            print(f" *** 目标工作表名称检查:Check 成功 - 指定名称: {target_sheet_name}")

        # 处理 sort_columns 参数
        if sort_columns is None or not isinstance(sort_columns, list):
            sort_columns = []
            print(f" *** 排序列参数检查:Check 成功 - 未指定排序列或参数无效，将不进行排序")
        else:
            print(f" *** 排序列参数检查:Check 成功 - 排序列: {sort_columns}")

        # 初始化用于存储合并数据的结构
        all_headers = []  # 存储所有遇到的表头
        merged_data = []  # 存储所有行的数据（列表的列表）
        print(f" *** 合并数据结构初始化:Init 成功")

        # --- 步骤 2: 读取并合并源数据 ---
        print(f" *** 开始处理源数据列表...")
        for item in source_sheet_list:
            # 根据修正后的格式检查元素
            if not isinstance(item, dict) or len(item) != 1:
                print(f" *** 源列表元素格式检查:Check 失败 - 元素格式错误: {item}")
                raise ValueError(
                    f"source_sheet_list 中的元素必须是只包含一个键值对的字典，格式为 {{'file_name': 'sheet_name'}}。错误元素: {item}")

            # 获取唯一的键值对
            src_file_name, src_sheet_name = next(iter(item.items()))

            # 验证键和值是否为字符串
            if not isinstance(src_file_name, str) or not isinstance(src_sheet_name, str):
                print(f" *** 源列表元素键值类型检查:Check 失败 - 键和值必须是字符串。错误元素: {item}")
                raise ValueError(f"source_sheet_list 中的字典键和值都必须是字符串。错误元素: {item}")

            src_file_path = os.path.join(source_directory, src_file_name)

            print(f" *** 解析源项:Check 成功 - 文件: {src_file_name}, 工作表: {src_sheet_name}")

            # 检查源文件是否存在
            if not os.path.exists(src_file_path):
                print(f" *** 源文件存在性检查:Check 失败 - 文件未找到: {src_file_path}")
                raise FileNotFoundError(f"在目录 '{source_directory}' 中未找到源文件: {src_file_name}")

            # 打开源工作簿
            try:
                src_wb = load_workbook(filename=src_file_path, read_only=True, data_only=True)
                print(f" *** 加载源工作簿:Check 成功 - 已打开: {src_file_name}")
            except Exception as e:
                print(f" *** 加载源工作簿:Check 失败 - 打开文件失败: {src_file_name}, 错误: {e}")
                raise e

            # 检查源工作表是否存在
            if src_sheet_name not in src_wb.sheetnames:
                src_wb.close()
                print(f" *** 源工作表存在性检查:Check 失败 - 工作表未找到: {src_sheet_name} in {src_file_name}")
                raise ValueError(f"在文件 '{src_file_name}' 中未找到工作表: {src_sheet_name}")

            src_ws = src_wb[src_sheet_name]
            print(f" *** 加载源工作表:Check 成功 - 已加载: {src_sheet_name}")

            # 获取源数据
            rows_iter = src_ws.iter_rows(values_only=True)

            try:
                # 尝试获取第一行作为表头
                header_row = next(rows_iter)
                # 处理可能的空表或只有表头的情况
                if header_row and any(cell is not None for cell in header_row):
                    current_headers = [str(cell) if cell is not None else '' for cell in header_row]
                else:
                    current_headers = []
                    # 如果第一行是空的或None，回退到没有表头的情况
                    # 重新获取迭代器，因为next()已经消费了第一行
                    rows_iter = src_ws.iter_rows(values_only=True)
            except StopIteration:
                # 工作表完全为空
                current_headers = []
                print(f" *** 源工作表内容检查:Check 成功 - 工作表为空: {src_sheet_name}")

            # 如果源有表头
            if current_headers:
                print(f" *** 源工作表表头检查:Check 成功 - 检测到表头: {current_headers}")
                # 更新全局表头列表
                for h in current_headers:
                    if h not in all_headers:
                        all_headers.append(h)
                header_map = {h: i for i, h in enumerate(current_headers)}  # 源表头到其索引的映射
            else:
                print(f" *** 源工作表表头检查:Check 成功 - 未检测到表头")
                header_map = {}

            row_index = 1  # 从第一行（或第二行，如果第一行是表头）开始计数
            added_rows_count = 0
            # 遍历源工作表的每一行（跳过表头行，如果有的话）
            for row_data in rows_iter:
                row_index += 1
                # 创建一个与总表头等长的新行，初始为空
                new_row = [''] * len(all_headers)

                # 填充数据
                for src_col_idx, cell_value in enumerate(row_data):
                    # 获取源表头（如果存在）
                    src_header = current_headers[src_col_idx] if src_col_idx < len(current_headers) else None

                    if src_header and src_header in all_headers:
                        # 如果源列有表头且该表头在总表头中，放入对应位置
                        global_col_idx = all_headers.index(src_header)
                        new_row[global_col_idx] = str(cell_value) if cell_value is not None else ''
                    elif not current_headers:
                        # 如果源表没有表头，则按列索引直接映射
                        # 如果列索引超出了当前总表头长度，需要扩展
                        while len(all_headers) <= src_col_idx:
                            new_header = f"Col_{len(all_headers) + 1}"
                            all_headers.append(new_header)
                            # 所有已存在的行也需要扩展
                            for r in merged_data:
                                r.append('')
                        new_row[src_col_idx] = str(cell_value) if cell_value is not None else ''
                    else:
                        # 如果源表头不在总表头中（新表头），则添加到末尾
                        # 或者源行数据比表头长（数据不规范），也按列索引处理
                        if src_header:
                            if src_header not in all_headers:
                                all_headers.append(src_header)
                                # 所有已存在的行也需要增加一列
                                for r in merged_data:
                                    r.append('')
                        # 确保new_row足够长
                        while len(new_row) < len(all_headers):
                            new_row.append('')
                        # 放入数据
                        global_col_idx = len(all_headers) - 1  # 放在最后一列
                        new_row[global_col_idx] = str(cell_value) if cell_value is not None else ''

                # 将处理好的行添加到合并数据中
                merged_data.append(new_row)
                added_rows_count += 1
                print(f" *** {src_file_name}::{src_sheet_name}.row=={row_index} ||-> add")

            src_wb.close()
            print(f" *** 关闭源工作簿:Check 成功 - 已关闭: {src_file_name}")

            # --- 步骤 3: 去重 ---
            # 简单的去重：将现有数据存入一个集合（基于元组，因为列表不可哈希）
            # 然后清空列表，再从集合中取回，最后再转回列表。这会移除完全相同的行。
            # 注意：这会改变原有行的顺序。
            if merged_data:
                initial_count = len(merged_data)
                unique_data_set = set(tuple(row) for row in merged_data)
                merged_data.clear()
                merged_data.extend(list(row) for row in unique_data_set)
                final_count = len(merged_data)
                duplicates_removed = initial_count - final_count
                print(f" *** {src_file_name}::{src_sheet_name} ||| redup=={duplicates_removed}")
            else:
                print(f" *** {src_file_name}::{src_sheet_name} ||| redup==0")

            print(f" *** {src_file_name}::{src_sheet_name} ||-> +++")

        # --- 步骤 4: 排序 ---
        if sort_columns and merged_data:
            print(f" *** 开始按指定列排序: {sort_columns}")

            # 创建列名到索引的映射
            header_to_index = {header: idx for idx, header in enumerate(all_headers)}

            # 构建排序键函数
            def sort_key(row):
                key = []
                for col in sort_columns:
                    if col in header_to_index:
                        # 获取该列的值用于排序
                        col_idx = header_to_index[col]
                        key.append(row[col_idx])
                    else:
                        # 如果指定的列不存在，使用空字符串作为默认值
                        key.append('')
                return key

            # 按照指定的列进行排序
            merged_data.sort(key=sort_key)
            print(f" *** 数据排序完成")

        # --- 步骤 5: 写入目标文件 ---
        print(f" *** 开始写入合并后的数据到目标文件...")

        # 确定最终的目标工作表名称
        final_sheet_name = target_sheet_name
        # 打开或创建目标工作簿
        if os.path.exists(target_file_path):
            try:
                target_wb = load_workbook(filename=target_file_path)
                print(f" *** 加载目标工作簿:Check 成功 - 文件已存在，已加载: {target_file_path}")
            except Exception as e:
                print(f" *** 加载目标工作簿:Check 失败 - 加载现有文件失败: {target_file_path}, 错误: {e}")
                # 如果加载失败，创建一个新的
                target_wb = Workbook()
                target_wb.remove(target_wb.active)  # 删除默认创建的Sheet
        else:
            target_wb = Workbook()
            target_wb.remove(target_wb.active)  # 删除默认创建的Sheet
            print(f" *** 创建目标工作簿:Init 成功 - 文件不存在，已创建新工作簿")

        # 处理目标工作表名称冲突
        if not final_sheet_name:
            sheet_counter = 1
            while f"Sheet{sheet_counter}" in target_wb.sheetnames:
                sheet_counter += 1
            final_sheet_name = f"Sheet{sheet_counter}"
            print(f" *** 目标工作表名称初始化:Init 成功 - 自动命名为: {final_sheet_name}")
        else:
            # 如果名称已存在，openpyxl的create_sheet会自动处理（添加数字后缀）
            # 但根据需求，我们需要覆盖，所以先删除同名的
            if final_sheet_name in target_wb.sheetnames:
                del target_wb[final_sheet_name]
                print(f" *** 目标工作表存在性检查:Check 成功 - 已删除同名工作表以准备覆盖: {final_sheet_name}")

        target_ws = target_wb.create_sheet(title=final_sheet_name)
        print(f" *** 创建/覆盖目标工作表:Check 成功 - 已创建/清空工作表: {final_sheet_name}")

        # 写入表头
        if all_headers:
            target_ws.append(all_headers)
            print(f" *** 写入表头:Check 成功 - 表头: {all_headers}")
        else:
            print(f" *** 写入表头:Check 成功 - 无表头数据")

        # 写入数据行
        for data_row in merged_data:
            target_ws.append(data_row)
        print(f" *** 写入数据行:Check 成功 - 共写入 {len(merged_data)} 行数据")

        # 保存目标工作簿
        try:
            target_wb.save(target_file_path)
            target_wb.close()
            print(f" *** 保存目标工作簿:Check 成功 - 数据已保存至: {target_file_path}")
        except Exception as e:
            target_wb.close()
            print(f" *** 保存目标工作簿:Check 失败 - 保存文件失败: {target_file_path}, 错误: {e}")
            raise e

        print(f" *** 整个合并过程完成:Check 成功 - 最终文件路径: {target_file_path}")
        return target_file_path

    except (ValueError, FileNotFoundError) as e:
        # 重新抛出已知的特定异常
        raise e
    except Exception as e:
        # 捕获并处理其他所有未预期的异常
        print(f" *** 操作过程中发生未预期的错误:Error - {e}")
        raise e  # 重新抛出异常，让调用者知道发生了错误

from openpyxl import load_workbook
import os

def excel_XLSX_blank_AutoDelete(file_path, sheet_names=None):
    """
    在Windows系统环境下，对指定的.xlsx格式Excel文件中的指定数据表，
    自动检测并删除完全空白的行和列，并将更改保存回原文件。

    参数:
    file_path (str): Excel文件的路径（相对路径或绝对路径）。不能为空。
    sheet_names (list, optional): 需要处理的数据表名称列表。
                                  如果为空或None，则处理文件中的所有数据表。

    返回:
    dict: 包含删除操作统计信息的字典。
          格式: {"TOTAL": 总删除数, "Delete_row": 删除的行数, "Delete_column": 删除的列数}

    异常:
    ValueError: 如果 file_path 为空或文件不存在。
    Exception: 读取、处理或保存文件时可能发生的其他错误。
    """
    # --- 初始化与检查 ---
    try:
        # 1. 检查第一个参数 file_path
        if not file_path:
            print(" *** 参数检查:file_path 为空 ||-||-|| 失败 ")
            raise ValueError("Excel文件路径 (file_path) 不能为空。")

        if not os.path.exists(file_path):
            print(f" *** 参数检查:file_path 文件不存在 ({file_path}) ||-||-|| 失败 ")
            raise ValueError(f"指定的Excel文件不存在: {file_path}")

        print(" *** 参数检查:file_path 成功 ")

        # 2. 检查并处理第二个参数 sheet_names
        # 如果 sheet_names 为空 (None, [], ''), 则设为 None 以便后续处理所有表
        if not sheet_names:
            sheet_names = None
            print(" *** 参数检查:sheet_names |-> 未指定或为空，将处理所有数据表 ||-||-|| 成功 ")
        else:
            # 确保 sheet_names 是一个列表
            if not isinstance(sheet_names, list):
                print(" *** 参数检查:sheet_names |-> 类型非列表，尝试转换 ||-||-|| 成功 ")
                sheet_names = list(sheet_names)
            print(" *** 参数检查:sheet_names 成功 ")

        # --- 加载Excel文件 ---
        print(f" *** 文件加载:load_workbook ({file_path}) ... ")
        workbook = load_workbook(filename=file_path)
        print(" *** 文件加载:load_workbook 成功 ")

        # --- 确定需要处理的数据表 ---
        sheets_to_process = []
        if sheet_names is None:
            # 如果未指定表名，则处理所有表
            sheets_to_process = workbook.sheetnames
            print(f" *** 数据表确定 |-> 处理所有表: {sheets_to_process} ||-||-|| 成功 ")
        else:
            # 检查指定的表名是否在工作簿中存在
            existing_sheets = workbook.sheetnames
            for name in sheet_names:
                if name in existing_sheets:
                    sheets_to_process.append(name)
                else:
                    print(f" *** 数据表确定 |-> 警告: 数据表 '{name}' 不存在于文件中，将被跳过。 ||-||-|| 成功 ")
            print(f" *** 数据表确定 |-> 确认处理表: {sheets_to_process} ||-||-|| 成功 ")

        if not sheets_to_process:
            print(" *** 数据表确定 |-> 错误: 没有有效的数据表需要处理。 ||-||-|| 失败 ")
            raise ValueError("没有找到需要处理的有效数据表。")

        # --- 初始化统计信息 ---
        stats = {"TOTAL": 0, "Delete_row": 0, "Delete_column": 0}
        print(" *** 统计初始化:stats 成功 ")

        # --- 遍历并处理每个数据表 ---
        for sheet_name in sheets_to_process:
            print(f" *** 开始处理数据表:{sheet_name} ... ")
            sheet = workbook[sheet_name]

            # --- 删除空白行 ---
            # 从最后一行开始向上遍历，避免删除行后索引变化导致的问题
            rows_to_delete = []
            max_row = sheet.max_row
            max_col = sheet.max_column

            if max_row == 1 and max_col == 1 and (
                    sheet.cell(row=1, column=1).value is None or sheet.cell(row=1, column=1).value == ""):
                # 特殊情况：只有一个空白单元格
                rows_to_delete.append(1)
            else:
                for row_num in range(max_row, 0, -1):  # 从最大行号到1
                    is_blank_row = True
                    for col_num in range(1, max_col + 1):
                        cell_value = sheet.cell(row=row_num, column=col_num).value
                        # 判断单元格是否为空 (None 或 空字符串)
                        if cell_value is not None and cell_value != "":
                            is_blank_row = False
                            break
                    if is_blank_row:
                        rows_to_delete.append(row_num)

            for row_index in rows_to_delete:
                sheet.delete_rows(row_index)
                print(f" *** {os.path.basename(file_path)}::{sheet_name}_blank.row=={row_index} ||-> delete ")
                stats["Delete_row"] += 1
                stats["TOTAL"] += 1

            print(f" *** 数据表:{sheet_name} 空白行删除完成，共删除 {len(rows_to_delete)} 行。")

            # --- 删除空白列 ---
            # 同理，从最后一列开始向左遍历
            cols_to_delete = []
            # 重新获取删除行后的最大行列数
            max_row_after_row_del = sheet.max_row
            max_col_after_row_del = sheet.max_column

            if max_row_after_row_del == 1 and max_col_after_row_del == 1 and (
                    sheet.cell(row=1, column=1).value is None or sheet.cell(row=1, column=1).value == ""):
                # 特殊情况：删除行后只剩一个空白单元格
                cols_to_delete.append(1)
            else:
                for col_num in range(max_col_after_row_del, 0, -1):  # 从最大列号到1
                    is_blank_col = True
                    for row_num in range(1, max_row_after_row_del + 1):
                        cell_value = sheet.cell(row=row_num, column=col_num).value
                        # 修改空白单元格判断逻辑：检查是否为None或去除空白字符后为空字符串
                        if cell_value is not None:
                            # 将cell_value转换为字符串再判断
                            str_value = str(cell_value)
                            if str_value.strip():  # 如果去除首尾空白后还有内容，则不是空白列
                                is_blank_col = False
                                break
                    if is_blank_col:
                        cols_to_delete.append(col_num)

            # 因为 openpyxl 的 delete_cols 是基于当前列索引的，删除一列后，后续列索引会自动减一
            # 所以如果从大到小删，索引会乱。应该先排序，再从小到大删。
            # 但更简单的方法是，我们记录要删的列号，然后按从大到小的顺序删。
            # openpyxl 的 delete_cols(idx, amount=1) 是删除从 idx 开始的 amount 列
            # 所以我们按列号从大到小删，是安全的。
            cols_to_delete.sort(reverse=True)  # 降序排列
            for col_index in cols_to_delete:
                sheet.delete_cols(col_index)
                print(f" *** {os.path.basename(file_path)}::{sheet_name}_blank.column=={col_index} ||-> delete ")
                stats["Delete_column"] += 1
                stats["TOTAL"] += 1

            print(f" *** 数据表:{sheet_name} 空白列删除完成，共删除 {len(cols_to_delete)} 列。")
            print(f" *** 数据表:{sheet_name} 处理完毕。")

        # --- 保存更改 ---
        print(f" *** 文件保存:save ({file_path}) ... ")
        workbook.save(filename=file_path)
        print(" *** 文件保存:save 成功 ")

        # --- 返回统计信息 ---
        print(" *** 操作完成，返回统计信息。")
        return stats

    except ValueError as ve:
        # 捕获特定的值错误（如参数错误）
        print(f" *** 函数执行失败 (ValueError): {ve}")
        raise ve  # 重新抛出，让调用者处理
    except FileNotFoundError as fnfe:
        # 更具体的文件未找到错误
        print(f" *** 函数执行失败 (FileNotFoundError): {fnfe}")
        raise ValueError(f"文件未找到: {file_path}") from fnfe
    except Exception as e:
        # 捕获其他所有异常
        print(f" *** 函数执行失败 (未知错误): {e}")
        raise e  # 重新抛出，让调用者处理

import pandas as pd
import os
from typing import List, Optional

def excel_XLSX_content_merge(file_path: str, sheet_names: List[str], merge_columns: List[str]) -> Optional[str]:
    """
    将指定Excel文件中的指定数据表按照指定列进行内容合并
    
    参数:
    - file_path: Excel源文件的文件路径名（支持相对路径和绝对路径）
    - sheet_names: 需要合并处理的数据表名称列表，如果为空则处理所有数据表
    - merge_columns: 作为合并依据的表头名列表
    
    返回值:
    - 实际保存文件路径，如果操作失败则返回None
    """
    try:
        # 1. 初始化+检查
        # 检查file_path是否为空
        if not file_path or not isinstance(file_path, str):
            raise ValueError("file_path不能为空且必须为字符串")
        print(f" *** 检查文件路径:{'Check'} 成功 ")
        
        # 检查merge_columns是否为空
        if not merge_columns or not isinstance(merge_columns, list):
            raise ValueError("merge_columns不能为空且必须为列表")
        print(f" *** 检查合并列:{'Check'} 成功 ")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        print(f" *** 检查文件存在:{'Check'} 成功 ")
        
        # 检查sheet_names是否为空，如果为空则获取所有sheet名称
        if not sheet_names or not isinstance(sheet_names, list):
            # 读取Excel文件获取所有sheet名称
            all_sheets = pd.ExcelFile(file_path).sheet_names
            sheet_names = all_sheets
            print(f" *** 检查数据表名称:{'Check'} |-> 使用默认所有数据表: {all_sheets} ||-||-|| 成功 ")
        else:
            print(f" *** 检查数据表名称:{'Check'} 成功 ")
        
        # 2. 读取指定Excel文件数据表内容
        excel_file = pd.ExcelFile(file_path)
        
        # 检查指定的数据表是否存在于文件中
        for sheet_name in sheet_names:
            if sheet_name not in excel_file.sheet_names:
                raise ValueError(f"数据表不存在: {sheet_name}")
        
        # 初始化结果字典，用于保存每个sheet的处理结果
        processed_sheets = {}
        print(f" *** 读取Excel数据表:{'Init'} 成功 ")
        
        # 3. 对每个数据表进行合并处理
        for sheet_name in sheet_names:
            print(f" *** 处理数据表: {sheet_name}:{'Process'} 开始 ")
            
            # 读取当前数据表
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f" *** 读取数据表 {sheet_name}:{'Read'} 成功 ")
            
            # 检查merge_columns中的列是否都在当前数据表中存在
            missing_columns = [col for col in merge_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"数据表 {sheet_name} 中不存在以下列: {missing_columns}")
            
            # 根据指定的列进行分组并合并
            # 首先，根据merge_columns进行分组
            grouped = df.groupby(merge_columns, dropna=False).first().reset_index()
            
            # 保存处理后的数据表
            processed_sheets[sheet_name] = grouped
            print(f" *** 合并数据表 {sheet_name}:{'Merge'} 成功 ")
        
        # 4. 将修改后的内容保存回源Excel文件
        # 使用ExcelWriter来写入多个sheet
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for sheet_name, processed_df in processed_sheets.items():
                processed_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f" *||* {os.path.basename(file_path)}::{sheet_name} ")
        
        print(f" *** 保存Excel文件:{'Save'} 成功 ")
        return file_path
        
    except Exception as e:
        print(f" *** 错误: {str(e)} ")
        return None


def list_Process_Rule_0(input_list, deduplicate=True, split_conditions=None, sort_result=True):
    """
    对输入的list变量进行拆分整理后返回
    
    参数:
    - input_list (list): 需要处理的list变量，不能为空
    - deduplicate (bool): 是否需要去重，默认为True
    - split_conditions (list): 作为拆分依据的条件列表，元素必须为字符串类型
    - sort_result (bool): 是否需要排序，默认为True
    
    返回:
    - list: 处理后的列表
    """
    try:
        # 1. 初始化+检查
        # 检查第一个参数是否为空或不存在
        if input_list is None or not isinstance(input_list, list) or len(input_list) == 0:
            raise ValueError("输入的list不能为空或不存在")
        
        print(" *** 参数检查:Check 成功 ")
        
        # 检查第二个参数是否为空，如果为空则使用默认值True
        if deduplicate is None:
            deduplicate = True
            print(" *** 去重参数:Init |-> 使用默认值True ||-||-|| 成功 ")
        else:
            print(" *** 去重参数:Init 成功 ")
        
        # 检查第三个参数是否为空，如果为空则设置为空列表
        if split_conditions is None:
            split_conditions = []
            print(" *** 分割条件:Init |-> 使用空列表(不进行分割) ||-||-|| 成功 ")
        elif not isinstance(split_conditions, list):
            raise ValueError("分割条件必须是list类型")
        else:
            # 验证分割条件中的所有元素都是字符串类型
            for condition in split_conditions:
                if not isinstance(condition, str):
                    raise ValueError("分割条件列表中的所有元素必须为string字符串类型")
            print(" *** 分割条件:Init 成功 ")
        
        # 检查第四个参数是否为空，如果为空则使用默认值True
        if sort_result is None:
            sort_result = True
            print(" *** 排序参数:Init |-> 使用默认值True ||-||-|| 成功 ")
        else:
            print(" *** 排序参数:Init 成功 ")
        
        # 初始化结果列表、中间临时列表和中间记录列表
        result_list = []
        temp_list = []
        record_list = []
        print(" *** 结果列表初始化:Init 成功 ")
        print(" *** 中间临时列表初始化:Init 成功 ")
        print(" *** 中间记录列表初始化:Init 成功 ")
        
        # 2. 如果需要去重，则对输入的list进行去重操作
        if deduplicate:
            # 使用set去重，但保持元素的原始类型，因此需要特殊处理
            seen = set()
            temp_list = []
            for item in input_list:
                # 将元素转换为可哈希的表示形式进行去重判断
                item_repr = repr(item)
                if item_repr not in seen:
                    seen.add(item_repr)
                    temp_list.append(item)
            print(" *** 去重操作:Process 成功 ")
        else:
            # 如果不需要去重，直接复制原列表
            temp_list = input_list[:]
            print(" *** 不进行去重操作:Process 成功 ")
        
        # 3. 如果分割条件不为空，则对中间临时列表进行分割处理
        if split_conditions:
            for item in temp_list:
                # 检查当前元素是否为字符串类型
                if isinstance(item, str):
                    # 遍历分割条件，查找匹配的分割符
                    split_occurred = False
                    current_str = item
                    
                    # 按长度从长到短排序分割条件，避免短条件先匹配影响长条件
                    sorted_conditions = sorted(split_conditions, key=len, reverse=True)
                    
                    for condition in sorted_conditions:
                        if condition in current_str:
                            # 使用指定条件分割字符串
                            parts = current_str.split(condition)
                            # 过滤空字符串并添加到记录列表
                            for part in parts:
                                if part:  # 只添加非空部分
                                    record_list.append(part)
                                    print(f" *** 当前分割得到子字符串元素: {part}")
                            split_occurred = True
                            break  # 找到一个匹配条件后就不再继续匹配其他条件
                    
                    # 如果没有找到匹配的分割条件，则直接添加原字符串
                    if not split_occurred:
                        record_list.append(current_str)
                        print(f" *** 当前分割得到子字符串元素: {current_str}")
                else:
                    # 如果当前元素不是字符串类型，直接添加到记录列表
                    record_list.append(item)
                    print(f" *** 当前元素非字符串，直接添加: {item}")
        else:
            # 如果没有分割条件，则直接将临时列表复制到记录列表
            record_list = temp_list[:]
            print(" *** 无分割条件，直接复制到记录列表:Process 成功 ")
        
        # 4. 将中间记录列表的元素添加到结果列表
        result_list = record_list[:]
        print(" *** 记录列表复制到结果列表:Process 成功 ")
        
        # 如果需要去重，则对结果列表进行去重操作
        if deduplicate:
            seen = set()
            deduplicated_list = []
            for item in result_list:
                item_repr = repr(item)
                if item_repr not in seen:
                    seen.add(item_repr)
                    deduplicated_list.append(item)
            result_list = deduplicated_list
            print(" *** 结果列表去重:Process 成功 ")
        
        # 如果需要排序，则对结果列表进行字典升序排序
        if sort_result:
            # 对于非字符串元素，先转换为字符串再排序
            result_list.sort(key=lambda x: str(x))
            print(" *** 结果列表排序:Process 成功 ")
        
        # 5. 返回处理后的列表
        print(f" *** 处理后得到的list列表: {result_list}")
        return result_list
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        raise e


import json

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

import json
import os
from typing import Union, List, Dict, Any

def write_to_json_AnyLevel(file_path: str, key_path: List[str], value: Union[List, str, Dict, bool, int] = None, mode: str = "update") -> bool:
    """
    Windows系统环境下通过python将内容写入指定json文件的任意层级的指定键值对的值
    
    参数:
    - file_path: string字符串，代表作为目标写入的json文件的文件路径名
    - key_path: list列表，代表目标键值对的所在层级以及键名称
    - value: 需要被写入指定键值对的数据内容，默认为None
    - mode: string字符串，写入方式，"update"或"add"，默认为"update"
    
    返回值:
    - bool: 操作是否成功
    """
    try:
        # 1. 初始化+检查
        # 检查第1个参数file_path是否为空
        if not file_path or not isinstance(file_path, str):
            print(" *** file_path检查:Init\\Check 失败 - 参数为空或类型错误 ***")
            raise ValueError("file_path参数不能为空且必须为字符串类型")
        print(" *** file_path检查:Init\\Check 成功 ***")

        # 检查第2个参数key_path是否为空
        if not key_path or not isinstance(key_path, list):
            print(" *** key_path检查:Init\\Check 失败 - 参数为空或类型错误 ***")
            raise ValueError("key_path参数不能为空且必须为列表类型")
        print(" *** key_path检查:Init\\Check 成功 ***")

        # 检查第3个参数value，如果为空则设为None
        if value is None:
            print(" *** value检查:Init\\Check |-> 使用默认值None ||-||-|| 成功 ***")
        else:
            print(" *** value检查:Init\\Check 成功 ***")

        # 检查第4个参数mode，如果为空则设为"update"
        if not mode:
            mode = "update"
            print(" *** mode检查:Init\\Check |-> 使用默认值update ||-||-|| 成功 ***")
        elif mode not in ["update", "add"]:
            print(" *** mode检查:Init\\Check 失败 - 参数值不合法 ***")
            raise ValueError("mode参数必须为'update'或'add'")
        else:
            print(" *** mode检查:Init\\Check 成功 ***")

        # 检查目标文件是否存在
        if not os.path.exists(file_path):
            print(f" *** 文件存在性检查:Init\\Check 失败 - 文件 {file_path} 不存在 ***")
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        print(f" *** 文件存在性检查:Init\\Check 成功 - 文件 {file_path} 存在 ***")

        # 初始化结果列表
        print(" *** 结果列表初始化:Init\\Check 成功 ***")

        # 2. 读取json文件并处理
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(" *** JSON文件读取:Init\\Check 成功 ***")

        # 3. 根据key_path检索目标键值对
        current_data = data
        path_length = len(key_path)
        
        # 遍历key_path中除最后一个元素外的所有元素，逐级向下检索
        for i in range(path_length - 1):
            key = key_path[i]
            if isinstance(current_data, dict) and key in current_data:
                # 如果当前层级是字典且键存在，继续向下一层级
                current_data = current_data[key]
                print(f" *** 键值对检索:Check |-> 匹配到键: {key} ||-||-|| 成功 ***")
            else:
                # 如果键不存在或当前层级不是字典，则需要创建新层级
                print(f" *** 键值对检索:Check |-> 未匹配到键: {key}, 开始创建层级 ||-||-|| 成功 ***")
                # 从当前位置开始，逐级创建缺失的键值对
                temp_data = current_data
                for j in range(i, path_length - 1):
                    next_key = key_path[j]
                    if j == path_length - 2:  # 倒数第二个键，其值应该是包含最后一个键的字典
                        # 根据mode决定如何设置初始值
                        if mode == "add":
                            temp_data[next_key] = {key_path[-1]: [value] if value is not None else [None]}
                        else:  # update模式
                            temp_data[next_key] = {key_path[-1]: value}
                    else:
                        temp_data[next_key] = {}
                        temp_data = temp_data[next_key]
                # 更新成功，直接保存并返回
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f" *||* {os.path.basename(file_path)}:{key_path[-1]}_创建并写入成功 ||-||-|| 成功 ***")
                return True

        # 检查最后一个键是否存在
        final_key = key_path[-1]
        if isinstance(current_data, dict) and final_key in current_data:
            # 键存在，根据mode进行更新或追加
            if mode == "update":
                current_data[final_key] = value
                print(f" *** 键值对更新:Check |-> 执行更新操作 ||-||-|| 成功 ***")
            else:  # add模式
                existing_value = current_data[final_key]
                # 检查现有值和新值的数据类型
                if type(existing_value) == type(value) and value is not None:
                    if isinstance(value, list):
                        current_data[final_key] = existing_value + value
                        print(f" *** 键值对追加:Check |-> 执行列表追加操作 ||-||-|| 成功 ***")
                    elif isinstance(value, dict):
                        current_data[final_key] = {**existing_value, **value}
                        print(f" *** 键值对追加:Check |-> 执行字典合并操作 ||-||-|| 成功 ***")
                    elif isinstance(value, str):
                        current_data[final_key] = existing_value + value
                        print(f" *** 键值对追加:Check |-> 执行字符串拼接操作 ||-||-|| 成功 ***")
                    elif isinstance(value, tuple):
                        current_data[final_key] = tuple(list(existing_value) + list(value))
                        print(f" *** 键值对追加:Check |-> 执行元组合并操作 ||-||-|| 成功 ***")
                    else:
                        # 其他类型，将原值转为列表，再添加新值
                        current_data[final_key] = [existing_value, value]
                        print(f" *** 键值对追加:Check |-> 执行通用追加操作 ||-||-|| 成功 ***")
                else:
                    # 不同类型，将原值转为列表，再添加新值
                    current_data[final_key] = [existing_value, value]
                    print(f" *** 键值对追加:Check |-> 执行类型不匹配追加操作 ||-||-|| 成功 ***")
        else:
            # 键不存在，根据mode决定如何创建
            if mode == "add":
                current_data[final_key] = [value] if value is not None else [None]
                print(f" *** 键值对创建:Check |-> 执行add模式创建操作 ||-||-|| 成功 ***")
            else:  # update模式
                current_data[final_key] = value
                print(f" *** 键值对创建:Check |-> 执行创建操作 ||-||-|| 成功 ***")

        # 4. 保存修改后的内容回源json文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f" *||* {os.path.basename(file_path)}:{final_key}_{mode}操作成功 ||-||-|| 成功 ***")
        
        return True

    except Exception as e:
        print(f" *** 函数执行失败:Error |-> {str(e)} ||-||-|| 失败 ***")
        return False

import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import warnings

def excel_sort_by_column(file_path, sheet_names, sort_columns, sort_direction):
    """
    对指定Excel文件中的数据表根据给定的列进行排序

    参数:
    file_path (str): Excel源文件的路径（支持相对路径和绝对路径）
    sheet_names (list): 需要排序的数据表名称列表，为空则对所有数据表排序
    sort_columns (list): 排序条件的表头名列表，为空则使用所有表头
    sort_direction (str): 排序方向，"up"为升序，"down"为降序，为空默认为升序

    返回:
    bool: 操作成功返回True，失败返回False
    """
    try:
        # 步骤1: 初始化+检查参数
        print(" *** 开始参数检查和初始化")

        # 检查第1个参数：文件路径
        if not file_path:
            raise ValueError("第1个参数（文件路径）不能为空")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的文件不存在: {file_path}")

        if not file_path.lower().endswith(('.xlsx', '.xls')):
            raise ValueError("文件必须是Excel格式（.xlsx 或 .xls）")

        print(" *** 文件路径检查:Check 成功")

        # 检查第2个参数：数据表名称
        if sheet_names is None or len(sheet_names) == 0:
            # 读取Excel文件获取所有数据表名称
            workbook = load_workbook(file_path, read_only=True)
            sheet_names = workbook.sheetnames
            workbook.close()
            print(f" *** 数据表名称参数:Init 成功 - 将处理所有数据表: {sheet_names}")
        else:
            print(f" *** 数据表名称参数:Check 成功 - 将处理指定数据表: {sheet_names}")

        # 检查第3个参数：排序表头
        if sort_columns is None or len(sort_columns) == 0:
            # 将在读取每个数据表时动态确定所有表头
            print(" *** 排序表头参数:Init 成功 - 将使用所有表头从左至右排序")
        else:
            print(f" *** 排序表头参数:Check 成功 - 排序条件: {sort_columns}")

        # 检查第4个参数：排序方向
        if not sort_direction:
            sort_direction = "up"
            print(" *** 排序方向参数:Init 成功 - 默认使用升序")
        elif sort_direction not in ["up", "down"]:
            raise ValueError("排序方向参数必须是 'up' 或 'down'")
        else:
            print(f" *** 排序方向参数:Check 成功 - 排序方向: {sort_direction}")

        # 转换排序方向为pandas参数
        ascending = True if sort_direction == "up" else False

        # 步骤2: 读取Excel文件并逐个处理数据表
        print(f" *** 开始读取Excel文件: {file_path}")

        # 使用openpyxl加载工作簿以保留格式
        workbook = load_workbook(file_path)

        for sheet_name in sheet_names:
            # 检查数据表是否存在
            if sheet_name not in workbook.sheetnames:
                print(f" *** 警告: 数据表 '{sheet_name}' 不存在，跳过处理")
                continue

            print(f" *** 正在处理数据表: {sheet_name}")

            # 步骤3: 读取数据表数据并进行排序
            # 使用pandas读取指定数据表，避免加载不必要的数据
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_excel(file_path, sheet_name=sheet_name)

            # 如果数据表为空，跳过处理
            if df.empty:
                print(f" *** 数据表 '{sheet_name}' 为空，跳过处理")
                continue

            # 确定实际使用的排序列
            actual_sort_columns = sort_columns if sort_columns else df.columns.tolist()

            # 检查排序列是否存在于数据表中
            missing_columns = [col for col in actual_sort_columns if col not in df.columns]
            if missing_columns:
                print(f" *** 警告: 数据表 '{sheet_name}' 中不存在列: {missing_columns}，将使用存在的列进行排序")
                actual_sort_columns = [col for col in actual_sort_columns if col in df.columns]

            if not actual_sort_columns:
                print(f" *** 警告: 数据表 '{sheet_name}' 中没有有效的排序列，跳过排序")
                continue

            # 执行排序操作
            print(f" *** 对数据表 '{sheet_name}' 按列 {actual_sort_columns} 进行{'升序' if ascending else '降序'}排序")
            df_sorted = df.sort_values(by=actual_sort_columns, ascending=ascending)

            # 清空原数据表内容
            sheet = workbook[sheet_name]
            sheet.delete_rows(1, sheet.max_row)

            # 将排序后的数据写回数据表
            for row_idx, row in enumerate(dataframe_to_rows(df_sorted, index=False, header=True), 1):
                for col_idx, value in enumerate(row, 1):
                    sheet.cell(row=row_idx, column=col_idx, value=value)

            # 步骤4: 记录处理完成
            print(f" *** {os.path.basename(file_path)}::{sheet_name} sorted")

        # 保存修改后的Excel文件
        workbook.save(file_path)
        workbook.close()

        print(" *** 所有数据表排序完成并已保存")
        return True

    except Exception as e:
        print(f" *** 错误: 排序过程中发生异常 - {str(e)}")
        return False

import pandas as pd
import os

def excel_column_to_list_Rule_1(file_path, sheet_names=None, header_conditions=None, match_mode="strict"):
    """
    从Excel文件中读取指定数据表的列数据，并根据条件筛选表头，将符合条件的列数据转换为列表返回
    
    参数:
    - file_path (str): Excel文件路径（支持相对路径和绝对路径）
    - sheet_names (list): 需要解析的数据表名称列表，为空则使用第一个数据表
    - header_conditions (list): 需要匹配的表头名条件列表，为空则遍历所有表头
    - match_mode (str): 匹配严格程度，"strict"为严格匹配，"simple"为宽松匹配，默认为"strict"
    
    返回:
    - list: 包含符合条件的列数据的列表
    """
    try:
        # 步骤1: 初始化+检查参数
        print(f" *** 参数检查:Init 成功 ***")
        
        # 检查第1个参数：文件路径
        if not file_path or not isinstance(file_path, str):
            raise ValueError("文件路径不能为空且必须为字符串类型")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的Excel文件不存在: {file_path}")
        
        print(f" *** 文件路径检查:Check 成功 ***")
        
        # 检查第2个参数：数据表名称列表
        if not sheet_names or not isinstance(sheet_names, list):
            print(f" *** 数据表名称检查:Check |-> 使用默认第一个数据表 ||-||-|| 成功 ***")
            sheet_names = None
        else:
            print(f" *** 数据表名称检查:Check 成功 ***")
        
        # 检查第3个参数：表头条件列表
        if not header_conditions or not isinstance(header_conditions, list):
            print(f" *** 表头条件检查:Check |-> 遍历所有表头 ||-||-|| 成功 ***")
            header_conditions = []
        else:
            print(f" *** 表头条件检查:Check 成功 ***")
        
        # 检查第4个参数：匹配模式
        if not match_mode or not isinstance(match_mode, str):
            print(f" *** 匹配模式检查:Check |-> 使用默认严格模式 ||-||-|| 成功 ***")
            match_mode = "strict"
        elif match_mode not in ["strict", "simple"]:
            print(f" *** 匹配模式检查:Check |-> 无效模式，使用默认严格模式 ||-||-|| 成功 ***")
            match_mode = "strict"
        else:
            print(f" *** 匹配模式检查:Check 成功 ***")
        
        # 初始化结果列表
        result_list = []
        print(f" *** 结果列表初始化:Init 成功 ***")
        
        # 步骤2: 读取Excel文件
        print(f" *** 读取Excel文件:Process 成功 ***")
        excel_file = pd.ExcelFile(file_path)
        
        # 如果没有指定数据表名称，则使用第一个数据表
        if sheet_names is None or len(sheet_names) == 0:
            sheet_names = [excel_file.sheet_names[0]]
        
        # 步骤3: 遍历指定的数据表
        for sheet_name in sheet_names:
            if sheet_name not in excel_file.sheet_names:
                print(f" *** 警告: 数据表 '{sheet_name}' 不存在于文件中，跳过 ***")
                continue
            
            print(f" *** 开始处理数据表: {sheet_name} ***")
            
            # 读取当前数据表
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 获取表头列表
            headers = df.columns.tolist()
            
            # 遍历每个表头
            for header in headers:
                # 判断表头是否符合条件
                is_match = False
                
                # 如果header_conditions为空，则所有表头都合法
                if len(header_conditions) == 0:
                    is_match = True
                else:
                    # 根据匹配模式进行匹配
                    for condition in header_conditions:
                        if match_mode == "strict":
                            # 严格模式：完全匹配（区分大小写）
                            if condition == header:
                                is_match = True
                                break
                        elif match_mode == "simple":
                            # 宽松模式：不区分大小写，或作为子字符串包含
                            if condition.lower() in header.lower() or condition.lower() == header.lower():
                                is_match = True
                                break
                
                # 打印匹配结果
                match_status = "合法" if is_match else "非法"
                print(f" *** {os.path.basename(file_path)}::{sheet_name}_{header} |-> {match_status} ***")
                
                # 如果匹配成功，则将该列数据添加到结果列表
                if is_match:
                    # 将该列数据转换为字符串并添加到结果列表
                    for cell_value in df[header].dropna():  # dropna() 移除空值
                        result_list.append(str(cell_value))
        
        # 步骤5: 打印结果数量并返回
        print(f" >>> 当前已读取到了 {len(result_list)} 个元素 <<< ")
        
        return result_list
    
    except Exception as e:
        print(f" *** 函数执行出错: {str(e)} ***")
        raise e


import pandas as pd
import os

def excel_column_process_Rule_0(file_path, sheet_names, header_conditions, match_mode="strict"):
    """
    对Excel文件中指定表头的数据列进行数据清洗
    
    参数:
    - file_path (str): 需要读取解析excel源文件的文件路径名，支持相对路径和绝对路径
    - sheet_names (list): 被读取的excel源文件需要解析的数据表名称
    - header_conditions (list): 数据表中需要解析的表头名条件
    - match_mode (str): 匹配的严格程度，'strict'表示严格匹配，'simple'表示宽松匹配，默认为'strict'
    
    返回:
    - DataFrame: 清洗后的数据
    """
    try:
        # 1. 初始化+检查
        # 检查file_path参数
        if not file_path or not isinstance(file_path, str):
            raise ValueError("文件路径不能为空且必须为字符串类型")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        
        print(f" *** 文件路径检查:Init\\Check 成功 ***")
        
        # 检查sheet_names参数，如果为空则使用默认值
        if not sheet_names or not isinstance(sheet_names, list):
            sheet_names = None
            print(f" *** 数据表名称检查:Init\\Check |-> 使用默认第一个数据表 ||-||-|| 成功 ***")
        else:
            print(f" *** 数据表名称检查:Init\\Check 成功 ***")
        
        # 检查header_conditions参数，如果为空则使用默认值
        if not header_conditions or not isinstance(header_conditions, list):
            header_conditions = []
            print(f" *** 表头条件检查:Init\\Check |-> 遍历所有表头 ||-||-|| 成功 ***")
        else:
            print(f" *** 表头条件检查:Init\\Check 成功 ***")
        
        # 检查match_mode参数，如果为空或无效则使用默认值
        if not match_mode or match_mode not in ["strict", "simple"]:
            match_mode = "strict"
            print(f" *** 匹配模式检查:Init\\Check |-> 使用默认严格模式 ||-||-|| 成功 ***")
        else:
            print(f" *** 匹配模式检查:Init\\Check 成功 ***")
        
        # 2. 根据file_path读取处理指定excel源文件以及对应数据表数据准备处理
        excel_data = pd.read_excel(file_path, sheet_name=sheet_names)
        
        # 确保excel_data始终是字典格式，便于统一处理
        if not isinstance(excel_data, dict):
            # 如果sheet_names为None或只指定一个sheet，pandas可能返回DataFrame而不是字典
            if sheet_names is None:
                # 获取第一个sheet的名称
                all_sheets = pd.ExcelFile(file_path).sheet_names
                first_sheet_name = all_sheets[0]
                excel_data = {first_sheet_name: excel_data}
            else:
                # 如果指定了一个sheet名称，pandas也会返回DataFrame
                excel_data = {sheet_names[0]: excel_data} if len(sheet_names) == 1 else excel_data
        
        print(f" *** Excel文件读取:Init\\Check 成功 ***")
        
        # 3. 遍历数据表，处理符合条件的表头所在列
        processed_count = 0
        
        for sheet_name, df in excel_data.items():
            print(f" *** 开始处理数据表: {sheet_name} ***")
            
            # 确保df是DataFrame类型
            if not isinstance(df, pd.DataFrame):
                print(f" *** 跳过数据表 {sheet_name}，因为数据格式不正确 ***")
                continue
                
            # 遍历表头
            for header in df.columns:
                # 判断表头是否符合条件
                is_match = False
                
                # 如果header_conditions为空，则所有表头都合法
                if not header_conditions:
                    is_match = True
                else:
                    # 根据match_mode进行匹配判断
                    for condition in header_conditions:
                        if match_mode == "strict":
                            # 严格模式：完全匹配（区分大小写）
                            if condition == str(header):
                                is_match = True
                                break
                        elif match_mode == "simple":
                            # 宽松模式：不区分大小写，且包含关系也匹配
                            if str(condition).lower() in str(header).lower() or str(condition).lower() == str(header).lower():
                                is_match = True
                                break
                
                # 输出当前表头匹配结果
                match_status = "合法" if is_match else "非法"
                print(f" *** {os.path.basename(file_path)}::{sheet_name}_{header} |-> {match_status} ***")
                
                # 如果表头匹配合法，则处理该列数据
                if is_match:
                    # 遍历该列的每个单元格
                    for idx, cell_value in enumerate(df[header]):
                        # 将单元格内容转换为字符串并去除首尾空格
                        cell_str = str(cell_value).strip() if pd.notna(cell_value) else ""
                        
                        # 识别是否含有字符"C"或者"D"
                        if "C" in cell_str:
                            df.at[idx, header] = "C"
                            processed_count += 1
                        elif "D" in cell_str:
                            df.at[idx, header] = "D"
                            processed_count += 1
                        else:
                            # 其他情况清空单元格内容
                            df.at[idx, header] = ""
                            processed_count += 1
        
        # 4. 将处理后的数据写回到原Excel文件中
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f" *** 数据已保存到文件: {file_path} ***")
        
        # 5. 输出处理结果数量
        print(f" >>> 当前已处理 {processed_count} 个元素 <<< ")
        
        # 如果只有一个sheet，返回DataFrame，否则返回字典
        if len(excel_data) == 1:
            return list(excel_data.values())[0]
        else:
            return excel_data
    
    except Exception as e:
        print(f"函数执行出错: {str(e)}")
        raise e


import pandas as pd
import os

def excel_sheet_process_Rule_0(file_path, sheet_names, header_conditions, match_mode="strict", filter_conditions=None):
    """
    Windows系统环境下通过python读取指定excel文件数据表，并根据其中指定条件表头所在数据列，进行单条件表头的数据行清洗。

    参数:
    - file_path (str): 需要读取解析excel源文件的文件路径名，支持相对路径和绝对路径
    - sheet_names (list): 被读取的excel源文件需要解析的数据表名称，如果为空则使用第一个数据表
    - header_conditions (list): 数据表中需要解析的表头名条件
    - match_mode (str): 匹配的严格程度，"strict"（严格）或"simple"（宽松），默认为"strict"
    - filter_conditions (list): 筛选过程中的条件，如果为空则默认所有数据行合法

    返回:
    - 无返回值，直接将处理后的表格保存回源excel文件
    """
    try:
        # 步骤1：初始化+检查
        # 检查第1个参数：文件路径是否为空或不存在
        if not file_path:
            raise ValueError("文件路径不能为空")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        print(f" *** 文件路径检查:Init 成功 ***")
        
        # 检查第2个参数：数据表名称列表，如果为空则使用默认值
        if not sheet_names:
            sheet_names = [None]  # None表示使用第一个数据表
            print(f" *** 数据表名称检查:Init |-> 使用默认数据表 ||-||-|| 成功 ***")
        else:
            print(f" *** 数据表名称检查:Init 成功 ***")
            
        # 检查第3个参数：表头条件列表，不能为空
        if not header_conditions:
            raise ValueError("表头条件列表不能为空")
        print(f" *** 表头条件检查:Init 成功 ***")
        
        # 检查第4个参数：匹配模式，默认为"strict"
        if match_mode not in ["strict", "simple"]:
            match_mode = "strict"
            print(f" *** 匹配模式检查:Init |-> 使用默认模式 strict ||-||-|| 成功 ***")
        else:
            print(f" *** 匹配模式检查:Init 成功 ***")
        
        # 检查第5个参数：筛选条件列表，如果为空则默认所有数据行合法
        if filter_conditions is None:
            filter_conditions = []
            print(f" *** 筛选条件检查:Init |-> 使用默认条件（所有数据行合法） ||-||-|| 成功 ***")
        else:
            print(f" *** 筛选条件检查:Init 成功 ***")

        # 步骤2：根据第1参数读取处理指定excel源文件以及对应数据表数据准备处理
        print(f" *** 读取Excel文件:Process 成功 ***")
        
        # 读取Excel文件，获取所有表名
        all_sheet_names = pd.ExcelFile(file_path).sheet_names
        print(f" *** Excel文件包含 {len(all_sheet_names)} 个数据表: {all_sheet_names} ***")
        
        # 如果sheet_names为空或为None，则使用第一个数据表
        if not sheet_names or sheet_names[0] is None:
            target_sheet = all_sheet_names[0]
        else:
            target_sheet = sheet_names[0]
            if target_sheet not in all_sheet_names:
                raise ValueError(f"指定的数据表 {target_sheet} 不存在于Excel文件中")
        
        print(f" *** 选择数据表:Process -> {target_sheet} 成功 ***")
        
        # 读取目标数据表
        df = pd.read_excel(file_path, sheet_name=target_sheet)
        print(f" *** 读取数据表 {target_sheet} 成功，共 {len(df)} 行数据 ***")

        # 步骤3：根据第2参数读取源文件的数据表内容进行处理
        # 遍历表头，根据第4参数指定的匹配严格程度，根据第3参数给出的条件对所有表头逐一进行匹配判断
        header_found = False
        matched_header = None
        
        for header in df.columns:
            header_match = False
            
            # 根据匹配模式进行表头匹配判断
            for condition in header_conditions:
                if match_mode == "strict":
                    # 严格模式：完全一样的字符串（区分大小写）
                    if str(header) == str(condition):
                        header_match = True
                        break
                elif match_mode == "simple":
                    # 宽松模式：不区分大小写，或作为子字符串
                    if str(condition).lower() in str(header).lower() or str(header).lower() in str(condition).lower():
                        header_match = True
                        break
            
            if header_match:
                header_found = True
                matched_header = header
                print(f" *** 找到匹配的表头: {header} ***")
                break
        
        if not header_found:
            raise ValueError(f"在数据表 {target_sheet} 中未找到匹配的表头")
        
        # 获取匹配表头所在的数据列
        target_column = df[matched_header]
        
        # 统计处理的数据行数
        processed_rows = 0
        
        # 遍历该表头所在数据列中的每一个单元格
        rows_to_drop = []
        for idx, cell_value in target_column.items():
            # 读取单元格内容为字符串，去除首尾空格
            cell_str = str(cell_value).strip() if pd.notna(cell_value) else ""
            
            cell_match = False
            if match_mode == "strict":
                # 严格模式：只有完全一样的字符串（区分大小写）才算匹配
                for condition in filter_conditions:
                    if cell_str == str(condition):
                        cell_match = True
                        break
            elif match_mode == "simple":
                # 宽松模式：不区分大小写或作为子字符串
                for condition in filter_conditions:
                    if str(condition).lower() in cell_str.lower() or cell_str.lower() in str(condition).lower():
                        cell_match = True
                        break
            
            # 判断单元格匹配结果并打印信息
            if cell_match:
                print(f" *** {os.path.basename(file_path)}::{target_sheet}_{matched_header}.row=={idx} ||-> 合法 ***")
                rows_to_drop.append(idx)  # 记录需要删除的行
            else:
                print(f" *** {os.path.basename(file_path)}::{target_sheet}_{matched_header}.row=={idx} ||-> 非法 ***")
            
            processed_rows += 1
        
        # 删除匹配的行
        df = df.drop(rows_to_drop)
        df = df.reset_index(drop=True)  # 重置索引，避免出现空白行
        
        print(f" >>> 当前已处理 {processed_rows} 个数据行 <<< ")
        
        # 步骤5：将处理后的表格保存回源excel文件源数据表
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=target_sheet, index=False)
        
        print(f" *** 保存处理后的数据表 {target_sheet} 到 {file_path} 成功 ***")
        
    except Exception as e:
        print(f" *** 函数执行出错: {str(e)} ***")
        raise e


import pandas as pd
import os

def excel_column_count_Rule_0(file_path, sheet_name, condition_header, match_mode='strict', keywords=None):
    """
    统计Excel文件中指定表头列符合关键词条件的行数
    
    参数:
        file_path (str): Excel文件的路径（支持相对和绝对路径）
        sheet_name (str): Excel中的工作表名称，若为空则使用第一个工作表
        condition_header (str): 用于统计的条件表头名称
        match_mode (str): 匹配模式，'strict'（严格）或'simple'（宽松），默认为'strict'
        keywords (list): 用作匹配的关键词列表，若为空则统计所有非表头行，默认为None
    
    返回:
        int: 符合条件的行数
    """
    try:
        # 步骤1：初始化和检查参数
        # 检查file_path是否为空
        if not file_path:
            raise ValueError("file_path 不能为空")
        print(f" *** file_path检查:Init 成功 ***")
        
        # 检查condition_header是否为空
        if not condition_header:
            raise ValueError("condition_header 不能为空")
        print(f" *** condition_header检查:Init 成功 ***")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        print(f" *** 文件存在检查:Check 成功 ***")
        
        # 如果sheet_name为空，设置为None，pandas会默认读取第一个工作表
        if not sheet_name:
            sheet_name = None
            print(f" *** sheet_name检查:Init |-> 使用第一个工作表 ||-||-|| 成功 ***")
        else:
            print(f" *** sheet_name检查:Init 成功 ***")
        
        # 如果match_mode为空或不是指定值，使用默认值
        if not match_mode or match_mode not in ['strict', 'simple']:
            match_mode = 'strict'
            print(f" *** match_mode检查:Init |-> 默认为'strict' ||-||-|| 成功 ***")
        else:
            print(f" *** match_mode检查:Init 成功 ***")
        
        # 如果keywords为空，设置为空列表
        if keywords is None:
            keywords = []
            print(f" *** keywords检查:Init |-> 无条件匹配 ||-||-|| 成功 ***")
        else:
            print(f" *** keywords检查:Init 成功 ***")

        # 初始化结果计数器
        result_count = 0
        print(f" *** 结果计数器初始化:Init 成功 ***")

        # 步骤2：读取Excel文件中的指定工作表
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # 获取实际使用的工作表名称
        if sheet_name is None:
            # 通过pandas获取实际读取的工作表名
            xl_file = pd.ExcelFile(file_path)
            actual_sheet_name = xl_file.sheet_names[0]
        else:
            actual_sheet_name = sheet_name
        print(f" *** 工作表读取:Check 成功，工作表名: {actual_sheet_name} ***")

        # 步骤3：检查条件表头是否存在
        if condition_header not in df.columns:
            raise KeyError(f"表头 '{condition_header}' 在工作表 '{actual_sheet_name}' 中不存在")
        print(f" *** 表头存在检查:Check 成功 ***")

        # 获取条件列的数据（不包含表头）
        condition_column = df[condition_header].dropna()  # 去除空值，但保留原始索引

        # 初始化临时记录列表
        temp_list = []

        # 遍历每一行数据
        for idx, cell_value in condition_column.items():
            # 将单元格值转换为字符串，便于比较
            cell_str = str(cell_value)
            
            # 如果keywords为空，所有行都合法
            is_valid = True
            if keywords:
                is_valid = False
                
                # 根据匹配模式判断合法性
                if match_mode == 'strict':
                    # 严格模式：完全匹配
                    if cell_str in keywords:
                        is_valid = True
                elif match_mode == 'simple':
                    # 宽松模式：子字符串或不区分大小写的匹配
                    cell_lower = cell_str.lower()
                    for keyword in keywords:
                        keyword_str = str(keyword)
                        if keyword_str.lower() in cell_lower or cell_lower in keyword_str.lower():
                            is_valid = True
                            break

            # 打印每行的判断结果
            status = "合法" if is_valid else "非法"
            print(f" *** {os.path.basename(file_path)}::{actual_sheet_name}_{condition_header}.row=={idx} ||-> {status} ***")
            
            # 如果行合法，将值加入临时列表并增加计数
            if is_valid:
                temp_list.append(cell_str)
                result_count += 1

        # 步骤6：打印最终统计结果
        print(f" >>> 当前统计了 {result_count} 个元素 <<< ")
        
        # 返回统计结果
        return result_count

    except Exception as e:
        print(f"发生错误: {e}")
        raise e


import pandas as pd
import os

def excel_column_count_Rule_1(file_path, sheet_name, condition_dict, match_type="strict"):
    """
    对指定Excel文件数据表按条件进行统计计数

    参数:
    file_path (str): Excel文件路径
    sheet_name (str): 工作表名称
    condition_dict (dict): 条件字典
    match_type (str): 匹配类型 ("strict" 或 "simple")

    返回:
    int: 符合条件的行数
    """
    try:
        # 步骤1：检查文件是否存在
        # 检查第1个参数是否为空
        if not file_path or not isinstance(file_path, str):
            raise ValueError("第1个参数（文件路径）不能为空或非字符串类型")
        print(f" *** 检查文件路径:{file_path} |-> Init 成功 ")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        print(f" *** 检查文件存在:{file_path} |-> Check 成功 ")

        # 检查第3个参数是否为空
        if condition_dict is None:
            condition_dict = {}
        print(f" *** 检查条件字典 |-> Init 成功 ")

        # 处理第2个参数，默认读取第一张表
        if not sheet_name or not isinstance(sheet_name, str):
            # 如果未指定工作表名称，读取Excel文件以获取第一个工作表的名称
            excel_file = pd.ExcelFile(file_path)
            if excel_file.sheet_names:
                sheet_name = excel_file.sheet_names[0]
                print(f" *** 检查表名 |-> 使用默认第一张表: {sheet_name} ||-||-|| 成功 ")
            else:
                raise ValueError("Excel文件中没有工作表")
        else:
            print(f" *** 检查表名:{sheet_name} |-> Init 成功 ")

        # 处理第4个参数，默认为"strict"
        if not match_type or not isinstance(match_type, str):
            match_type = "strict"
            print(f" *** 检查匹配类型 |-> 使用默认strict ||-||-|| 成功 ")
        elif match_type not in ["strict", "simple"]:
            match_type = "strict"
            print(f" *** 检查匹配类型 |-> 使用默认strict ||-||-|| 成功 ")
        else:
            print(f" *** 检查匹配类型:{match_type} |-> Init 成功 ")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到文件: {file_path}")

        # 步骤2：读取Excel文件的指定工作表
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        file_name = os.path.basename(file_path)

        # 步骤3：初始化计数器
        result_count = 0
        print(f" *** 初始化结果变量 |-> Init 成功 ")

        # 步骤4：遍历每一行数据
        for index, row in df.iterrows():
            is_valid_row = True

            # 遍历所有条件
            for column_name, keyword in condition_dict.items():
                # 检查列是否存在
                if column_name not in df.columns:
                    print(f"警告: 列 '{column_name}' 不存在于工作表 '{sheet_name}' 中")
                    is_valid_row = False
                    break

                # 获取单元格值
                cell_value = row[column_name]

                # 将cell_value和keyword都转换为字符串进行比较
                cell_str = str(cell_value) if cell_value is not None else ""
                keyword_str = str(keyword) if keyword is not None else ""

                # 根据匹配模式判断合法性
                if match_type == "strict":
                    # 严格匹配：完全相等
                    if cell_str != keyword_str:
                        is_valid_row = False
                        break
                elif match_type == "simple":
                    # 宽松匹配：包含或不区分大小写的包含
                    if keyword_str.lower() not in cell_str.lower():
                        is_valid_row = False
                        break

            # 如果当前行满足所有条件，则计数器加1
            if is_valid_row:
                result_count += 1
                print(
                    f" *** {file_name}::{sheet_name}_{list(condition_dict.keys())[0] if condition_dict else 'all'} |-> （合法.{result_count}）")
            else:
                print(
                    f" *** {file_name}::{sheet_name}_{list(condition_dict.keys())[0] if condition_dict else 'all'} |-> （非法）")

        # 步骤5：输出最终统计结果
        print(f" >>> 当前统计了 {result_count} 个元素 <<< ")

        # 返回统计结果
        return result_count

    except Exception as e:
        print(f"函数执行出错: {str(e)}")
        raise e


import pandas as pd
import os
from typing import List, Dict, Any, Union

import pandas as pd
import os

def excel_column_count_Rule_2(file_path, sheet_name, condition_headers):
    """
    Windows系统环境下通过python对指定excel文件数据表，按输入参数指定的条件进行多表头多条件的统计计数并返回dict类型的统计结果

    参数:
    - file_path: string, 需要读取解析excel源文件的文件路径名
    - sheet_name: string, excel源文件中需要被读取进行统计的数据表名称
    - condition_headers: list, 数据表中作为统计依据的条件表头

    返回:
    - dict: 统计结果
    """
    try:
        # 步骤1: 初始化+检查
        print(f" *** 参数检查:Init 成功 ")
        
        # 检查第一个参数是否为空
        if not file_path or not isinstance(file_path, str):
            raise ValueError("文件路径不能为空")
        print(f" *** 文件路径检查:Check 成功 ")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        print(f" *** 文件存在检查:Check 成功 ")
        
        # 检查第二个参数是否为空，如果为空则使用默认值
        if not sheet_name or not isinstance(sheet_name, str):
            sheet_name = 0  # 使用第一个工作表而不是None
            print(f" *** 表名检查:Check |-> 使用默认第一张表 ||-||-|| 成功 ")
        else:
            print(f" *** 表名检查:Check 成功 ")
        
        # 检查第三个参数是否为空，如果为空则使用默认值
        if not condition_headers or not isinstance(condition_headers, list):
            condition_headers = []
            print(f" *** 条件表头检查:Check |-> 使用默认所有行均合法 ||-||-|| 成功 ")
        else:
            print(f" *** 条件表头检查:Check 成功 ")
        
        # 初始化结果字典
        result = {"Result": {}}
        print(f" *** 结果初始化:Init 成功 ")
        
        # 步骤2: 读取指定的数据表内容准备统计
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name)
        # 确保获取的是DataFrame而不是包含多个表的字典
        if isinstance(df_raw, dict):
            # 如果返回的是字典，取第一个工作表
            df = list(df_raw.values())[0]
        else:
            df = df_raw
        print(f" *** 读取数据表:Init 成功 ")
        
        # 如果条件表头为空，则直接统计所有数据行数量（不包括表头）
        if not condition_headers:
            count = len(df)
            result["Result"] = count
            print(f" *** {os.path.basename(file_path)}::{sheet_name or '默认表'}_所有行 |-> {count}")
            print(f" *** 当前结果: {result}")
            return result
        
        # 步骤3: 按条件统计
        for index, row in df.iterrows():
            # 获取当前行的条件值
            current_dict = result["Result"]
            
            # 遍历条件表头（除了最后一个），构建嵌套字典结构
            for i, header in enumerate(condition_headers[:-1]):
                value = str(row[header])  # 将值转换为字符串作为键
                if value not in current_dict:
                    current_dict[value] = {}
                current_dict = current_dict[value]
            
            # 处理最后一个条件表头，进行计数
            last_header = condition_headers[-1]
            last_value = str(row[last_header])
            if last_value in current_dict:
                current_dict[last_value] += 1
            else:
                current_dict[last_value] = 1
            
            # 步骤4: 每统计一次，输出当前结果
            print(f" *** {os.path.basename(file_path)}::{sheet_name or '默认表'}_{last_header} |-> {current_dict[last_value]}")
        
        # 步骤5: 统计完后输出结果并返回
        print(f" *** 当前结果: {result}")
        return result
        
    except Exception as e:
        print(f"发生异常: {str(e)}")
        raise e


import pandas as pd
import os
from typing import Dict, List, Union

def excel_column_count_Rule_3(file_path: str, sheet_name: str, condition_columns: List[str], count_column: str) -> Dict:
    """
    对指定Excel文件数据表按条件进行统计计数并返回dict格式的键值对统计结果
    
    参数:
    - file_path: Excel源文件的文件路径名（支持相对路径和绝对路径）
    - sheet_name: Excel源文件中需要被读取进行统计的数据表名称
    - condition_columns: 作为统计条件组合的表头列表
    - count_column: 作为统计项的表头名
    
    返回:
    - dict格式的统计结果
    """
    try:
        # 步骤1: 初始化+检查
        # 检查第1个参数（文件路径）是否为空
        if not file_path or not isinstance(file_path, str):
            raise ValueError("第1个参数（文件路径）不能为空")
        print(f" *** 文件路径检查:Init|Check 成功 ")
        
        # 检查第4个参数（统计项表头）是否为空
        if not count_column or not isinstance(count_column, str):
            raise ValueError("第4个参数（统计项表头名）不能为空")
        print(f" *** 统计项表头检查:Init|Check 成功 ")
        
        # 检查目标文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的Excel文件不存在: {file_path}")
        print(f" *** 文件存在性检查:Init|Check 成功 ")
        
        # 检查第2个参数（数据表名称）是否为空，如果为空则使用默认值
        if not sheet_name or not isinstance(sheet_name, str):
            print(f" *** 数据表名称检查:Init|Check |-> 使用默认第一张表 ||-||-|| 成功 ")
            sheet_name = None
        else:
            print(f" *** 数据表名称检查:Init|Check 成功 ")
        
        # 检查第3个参数（统计条件表头列表）是否为空
        if not condition_columns or not isinstance(condition_columns, list):
            print(f" *** 统计条件表头检查:Init|Check |-> 无统计条件 ||-||-|| 成功 ")
            condition_columns = []
        else:
            print(f" *** 统计条件表头检查:Init|Check 成功 ")
        
        # 初始化结果字典
        result = {}
        print(f" *** 结果字典初始化:Init|Check 成功 ")
        
        # 步骤2: 读取Excel文件中指定的数据表
        if sheet_name is None:
            # 如果没有指定数据表名称，则读取第一张数据表
            df = pd.read_excel(file_path, sheet_name=0)
            sheet_name = pd.ExcelFile(file_path).sheet_names[0]  # 获取实际表名
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        # print(f" *** 读取数据表:{file_path.split('/')[-1].split('\\')[-1]}::{sheet_name} 成功 ")
        
        # 检查所需的列是否存在
        if count_column not in df.columns:
            raise KeyError(f"统计项表头 '{count_column}' 在数据表中不存在")
        
        if condition_columns:
            for col in condition_columns:
                if col not in df.columns:
                    raise KeyError(f"统计条件表头 '{col}' 在数据表中不存在")
        
        # 步骤3: 根据条件进行统计
        file_name = os.path.basename(file_path)
        
        if not condition_columns:
            # 没有统计条件，对统计项列进行求和
            sum_value = 0
            for value in df[count_column]:
                try:
                    # 尝试转换为数值，如果失败则按0处理
                    num_value = float(value) if pd.notna(value) else 0
                    sum_value += num_value
                except (ValueError, TypeError):
                    # 如果无法转换为数值，则按0处理
                    sum_value += 0
            
            # 转换结果为整数（如果适用）
            sum_value = convert_float_to_int(sum_value)
            
            result["Result"] = sum_value
            print(f" *** {file_name}::{sheet_name}_{count_column} |->| 无条件=={sum_value} ")
        else:
            # 有统计条件，按条件组合进行分组统计
            result["Result"] = {}
            
            # 遍历每一行数据
            for index, row in df.iterrows():
                # 构建条件组合的键路径
                current_dict = result["Result"]
                
                # 遍历所有条件列，构建嵌套字典结构
                for i, col in enumerate(condition_columns):
                    value = row[col]
                    try:
                        # 尝试转换为数值，如果失败则保持原值
                        if pd.notna(value):
                            value = float(value)
                        else:
                            value = 0
                    except (ValueError, TypeError):
                        # 如果无法转换为数值，则保持原值
                        pass
                    
                    # 如果是最后一个条件列，进行数值处理和求和
                    if i == len(condition_columns) - 1:
                        # 获取统计列的值
                        count_value = row[count_column]
                        try:
                            # 尝试转换为数值，如果失败则按0处理
                            num_count_value = float(count_value) if pd.notna(count_value) else 0
                        except (ValueError, TypeError):
                            num_count_value = 0
                            
                        # 转换结果为整数（如果适用）
                        num_count_value = convert_float_to_int(num_count_value)
                        
                        # 更新字典中的值
                        if str(value) in current_dict:
                            current_dict[str(value)] += num_count_value
                            
                            # 转换累加后的结果为整数（如果适用）
                            current_dict[str(value)] = convert_float_to_int(current_dict[str(value)])
                            
                        else:
                            current_dict[str(value)] = num_count_value
                    else:
                        # 如果不是最后一个条件列，继续构建嵌套结构
                        str_value = str(value)
                        if str_value not in current_dict:
                            current_dict[str_value] = {}
                        current_dict = current_dict[str_value]
                
                # 打印当前统计结果
                condition_str = " AND ".join([f"{col}={row[col]}" for col in condition_columns])
                print(f" *** {file_name}::{sheet_name}_{count_column} |->| <{condition_str}]=={num_count_value} ")
        
        # 步骤5: 打印并返回结果
        print(f" *** 当前结果键值对: {result} ")
        
        return result
    
    except Exception as e:
        print(f" *** 错误: {str(e)} ")
        raise e  

# 辅助函数：将浮点数转换为整数（如果小数部分为0）
def convert_float_to_int(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


import json
import os
from openpyxl import load_workbook
from typing import Dict, Any, Optional

def Json_to_excel_Rule_0(
    data_json_path: str,
    data_key: str,
    config_json_path: str,
    config_key: str,
    target_excel_path: str,
    target_sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    根据指定json文件中的参数引导，将指定json文件中的多级嵌套键值对结构的源数据填写到目标excel文件中的指定数据表
    
    Args:
        data_json_path (str): 需要读取解析json源文件的文件路径名
        data_key (str): 被读取的json源文件中作为填写数据的键值对的最高层级键名称
        config_json_path (str): 需要读取作为引导参数的json源文件的文件路径名
        config_key (str): 被读取的json源文件中作为引导参数的键值对的最高层级键名称
        target_excel_path (str): 作为填写目标的excel文件的文件路径名
        target_sheet_name (str, optional): 作为填写目标的excel源文件中的指定数据表名称
        
    Returns:
        Dict[str, Any]: 记录填写结果的字典
    """
    
    try:
        # *** 参数检查:Init 成功
        print(f" *** 参数检查:Init 成功")
        
        # 检查参数输入
        if not all([data_json_path, data_key, config_json_path, config_key, target_excel_path]):
            raise ValueError("必需参数不能为空")
            
        # 检查文件是否存在
        if not os.path.exists(data_json_path):
            raise FileNotFoundError(f"数据文件不存在: {data_json_path}")
        if not os.path.exists(config_json_path):
            raise FileNotFoundError(f"配置文件不存在: {config_json_path}")
        if not os.path.exists(target_excel_path):
            raise FileNotFoundError(f"目标Excel文件不存在: {target_excel_path}")
            
        # *** 文件检查:Check 成功
        print(f" *** 文件检查:Check 成功")
        
        # 读取数据文件
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
            
        # 读取配置文件
        with open(config_json_path, 'r', encoding='utf-8') as f:
            config_json = json.load(f)
            
        # *** 文件读取:Init 成功
        print(f" *** 文件读取:Init 成功")
        
        # 获取数据和配置
        data_dict = data_json.get(data_key, {})
        config_dict = config_json.get(config_key, {})
        
        if not data_dict:
            raise KeyError(f"在数据文件中未找到键: {data_key}")
        if not config_dict:
            raise KeyError(f"在配置文件中未找到键: {config_key}")
            
        # 加载目标Excel文件
        workbook = load_workbook(target_excel_path)
        
        # 处理sheet name
        if not target_sheet_name:
            target_sheet_name = workbook.sheetnames[0]
            
        # *** Sheet检查:Check 成功
        print(f" *** Sheet检查:Check 成功")
        
        worksheet = workbook[target_sheet_name]
        
        # 用于记录结果
        result = {
            "success_count": 0,
            "failures": []
        }
        
        # 递归函数用于处理嵌套字典的匹配和填写
        def process_nested_dicts(data_obj, config_obj, path=""):
            if isinstance(data_obj, dict) and isinstance(config_obj, dict):
                # 遍历数据字典
                for key, value in data_obj.items():
                    new_path = f"{path}.{key}" if path else key
                    
                    # 检查配置中是否有对应的键
                    if key in config_obj:
                        # 递归处理下一层
                        process_nested_dicts(value, config_obj[key], new_path)
            elif not isinstance(data_obj, dict) and not isinstance(config_obj, dict):
                # 到达最底层，进行匹配和填写
                try:
                    cell_address = config_obj  # 配置中的值应该是单元格地址
                    # 填写数据到Excel
                    worksheet[cell_address] = data_obj
                    print(f" *** {os.path.basename(target_excel_path)}::{target_sheet_name}_{cell_address} ||-> {data_obj}")
                    result["success_count"] += 1
                except Exception as e:
                    error_msg = f"填写数据时出错 {path}: {str(e)}"
                    result["failures"].append(error_msg)
                    print(f" *** 错误:{error_msg}")
            else:
                # 数据结构不匹配
                error_msg = f"数据结构不匹配: {path}"
                result["failures"].append(error_msg)
                print(f" *** 跳过:{error_msg}")
        
        # 开始处理数据
        process_nested_dicts(data_dict, config_dict)
        
        # 保存Excel文件
        workbook.save(target_excel_path)
        
        # *** 数据保存:Check 成功
        print(f" *** 数据保存:Check 成功")
        
        return result
        
    except Exception as e:
        print(f" *** 异常发生 |-> {str(e)}")
        raise e


###########################################################################################

from UI.GUI import excel_head_row_GUI_select
###

from UI.GUI import GUI_JSON_list_selector
###

from UI.GUI import GUI_XLSX_export_MultiCondition
###

from UI.GUI import GUI_XLSX_export_MultiCondition_MultiSort
###

from UI.GUI import GUI_XLSX_export_MultiCondition_MultiSort_RULE_0
###

###########################################################################################

Exclude_Folder_OR_files = [ "temp", "结果", "logs"]
current_time = {}
Target_sheets = [ "1", "2", "3", "4"]

###########################################################################################

if __name__ == '__main__':
    print_hi('PyCharm')
    
    # ------------------------------------------------------------------------------------------------

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

    ## 环境类型
    print("当前运行环境类型:", "打包环境\n" if check_if_bundled() else "开发环境\n")
    print("实际运行路径:", get_base_path())

    current_time_string = Time_dict_TO_string(time_dict=current_time,
                                              format_string="%Y-%m-%d_%H-%M-%S"
                                              )

    # 临时文件夹
    result = create_folder(folder_name="temp",
                            target_path=""
                            )
    print(result)
    print("")

    result = JSON_CleanUP(file_path=r"./temp/temp.json")
    print(result)
    print("")

    # 结果文件夹
    FINAL = create_folder(folder_name="自动统计填写结果"+current_time_string,
                           target_path=""
                           )
    print(FINAL)
    print("")
    
    ## 模板准备--------------------------------------------
    #
    temp = get_resource_path(r"config\config.json")
    print(temp)
    print("")
    
    try:
        file_Move_OR_Copy( source_file_path=temp, target_path=r".\temp", operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")
    
    #
    FINAL_1 = None
    temp = get_resource_path(r"config\第三方督查计划管控.xlsx")
    print(temp)
    print("")
    
    try:
        FINAL_1 = file_Move_OR_Copy( source_file_path=temp, target_path=FINAL, operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")
        
    #
    result = write_to_json(file_path=r"./temp/temp.json",
                      key_name="可选数据表",
                      data_content=Target_sheets,
                      write_mode="add"
                      )
    print(result)
    print("")
    
    # ------------------------------------------------------------------------------------------------
    print("\n######### ！！！准备完毕，输入运行参数！！！ #########\n")

    result = scan_XLS_then_XLSX(target_path=r"")
    print(result)
    print("")

    SourceExcel = excel_Scan_XLSX(
        directory_path=r"./",
        exclude_list=Exclude_Folder_OR_files
    )
    print(SourceExcel)
    print("！！！")

    ## 工作文件扫描
    for file in SourceExcel:
        temp_0 = excel_XLSX_Read_sheets(file_path= file)
        print(temp_0)
        print("")

        write_to_json(file_path=r"./temp/temp.json",
                      key_name="SourceFile",
                      data_content=temp_0,
                      write_mode="add"
                      )

    ## 源数据合并
    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="请选择需要处理的Excel源文件及其数据表"
    )
    print(MergeExcel)

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/源数据temp.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=[]
    )
    print(result)
    print("")

    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/源数据temp.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    result = excel_sort_by_column(file_path=r"./temp/源数据temp.xlsx",
                                  sheet_names= [],
                                  sort_columns= ["整改单编号", "建设单位", "项目类别"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    ## 数据筛选
    temp = excel_column_to_list_Rule_1(file_path=r"./temp/源数据temp.xlsx",
                                       sheet_names= [],
                                       header_conditions= ["督查人员"],
                                       match_mode="strict"
                                       )
    print(temp)
    print("")
    
    temp = list_Process_Rule_0(input_list=temp,
                               deduplicate=True,
                               split_conditions=[","],
                               sort_result=True
                               )
    print(temp)
    print("")
    
    result = write_to_json(file_path=r"./temp/temp.json",
                      key_name="督查人员all",
                      data_content=temp,
                      write_mode="add"
                      )
    print(result)
    print("")
    
    temp = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="督查人员all",
        window_title="请选择需要排除的督察人员"
    )
    print(temp)
    print("")
    
    result = write_to_json(file_path=r"./temp/temp.json",
                      key_name="排除人员",
                      data_content=temp,
                      write_mode="update"
                      )
    print(result)
    print("")
    
    # 数据筛选
    result = excel_sheet_process_Rule_0(file_path=r"./temp/源数据temp.xlsx",
                                        sheet_names= [],
                                        header_conditions= ["督查人员"],
                                        match_mode="strict",
                                        filter_conditions= temp
                                        )
    print(result)
    print("")
    
    result = excel_column_process_Rule_0(file_path=r"./temp/源数据temp.xlsx",
                                         sheet_names= [],
                                         header_conditions= ["违章代码"],
                                         match_mode="strict"
                                         )
    print(result)
    print("")
    
    # 数据统计
    result = excel_column_count_Rule_2(file_path=r"temp\源数据temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "督查形式", "建设单位", "项目类别"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "项目类型统计"],
        value=result["Result"],
        mode="update"
    )
    
    result = excel_column_count_Rule_2(file_path=r"temp\源数据temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "督查形式", "建设单位", "违章代码"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "违章代码统计"],
        value=result["Result"],
        mode="update"
    )
    
    # 数据填写
    temp = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="可选数据表",
        window_title="请选择需要填写的数据表"
    )
    print(temp)
    print("")
    
    if len(temp) == 1:
        temp = str(temp[0])
    else:
        raise ValueError("列表必须只包含一个元素")
    
    result = write_to_json(file_path=r"./temp/temp.json",
                      key_name="目标数据表",
                      data_content=temp,
                      write_mode="update"
                      )
    print(result)
    print("")
    
    result = Json_to_excel_Rule_0(data_json_path=r"temp\temp.json",
                                  data_key="项目类型统计",
                                  config_json_path=r"temp\config.json",
                                  config_key="项目类型统计",
                                  target_excel_path=FINAL + r"\第三方督查计划管控.xlsx",
                                  target_sheet_name=temp,
                                  )
    print(result)
    print("")
    
    result = Json_to_excel_Rule_0(data_json_path=r"temp\temp.json",
                                  data_key="违章代码统计",
                                  config_json_path=r"temp\config.json",
                                  config_key="违章代码统计",
                                  target_excel_path=FINAL + r"\第三方督查计划管控.xlsx",
                                  target_sheet_name=temp,
                                  )
    print(result)
    print("")
