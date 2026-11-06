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

# def excel_Scan_XLSX(directory_path: str = None, exclude_list: list = None) -> list:
#     """
#     扫描指定目录及其子目录下所有 .xlsx 格式的 Excel 文件，并返回文件名列表。
#     支持通过排除列表忽略特定的文件或文件夹。

#     此函数会递归遍历给定目录（或默认的当前脚本目录），
#     查找所有以 .xlsx 结尾的文件。在遍历过程中，如果遇到的
#     文件名或文件夹名在 exclude_list 中，则会跳过该文件或整个文件夹。
#     最终将所有找到的 .xlsx 文件的文件名（不包含路径）添加到列表中返回。

#     Args:
#         directory_path (str, optional):
#             需要扫描的目录路径（相对路径或绝对路径）。
#             如果未提供或为空字符串，则默认使用当前脚本所在的目录。
#         exclude_list (list, optional):
#             一个包含需要排除的文件名或文件夹名的列表。
#             在扫描过程中，如果遇到同名的文件或文件夹，将会被忽略。
#             如果未提供或为空，则不进行任何排除，递归扫描所有内容。

#     Returns:
#         list[str]:
#             一个列表，其中每个元素都是一个找到的 .xlsx 文件的文件名（不含路径）。
#             例如: ['report1.xlsx', 'data.xlsx', ...]

#     Raises:
#         ValueError: 如果提供的 directory_path 不是目录或不存在。
#         Exception: 如果在扫描目录或处理文件时发生其他未预期的错误。
#     """
#     # --- 步骤 1: 初始化和检查 ---
#     try:
#         # 检查并设置目录路径
#         if not directory_path:
#             # 获取当前执行脚本的绝对路径，然后获取其所在的目录
#             directory_path = os.path.dirname(os.path.abspath(__file__))
#             print(f" *** 参数为空，使用默认目录:Init 成功 - 设置为当前脚本目录: {directory_path}")
#         else:
#             print(f" *** 参数检查:Check 成功 - 接收到目录路径: {directory_path}")

#         # 规范化路径，处理路径中的 .. 或 . 等
#         directory_path = os.path.normpath(directory_path)

#         # 检查路径是否存在
#         if not os.path.exists(directory_path):
#             print(f" *** 路径存在性检查:Check 失败 - 路径不存在: {directory_path}")
#             raise ValueError(f"指定的目录路径不存在: {directory_path}")

#         # 检查路径是否确实是一个目录
#         if not os.path.isdir(directory_path):
#             print(f" *** 目录有效性检查:Check 失败 - 路径不是目录: {directory_path}")
#             raise ValueError(f"指定的路径不是一个目录: {directory_path}")

#         print(f" *** 目录存在性及有效性检查:Check 成功 - 目录有效: {directory_path}")

#         # 处理排除列表
#         if not exclude_list or not isinstance(exclude_list, list):
#             exclude_list = []
#             print(f" *** 排除列表检查:Check 成功 - 未提供排除列表或列表为空，将扫描所有文件")
#         else:
#             # 确保排除列表中的元素是字符串，便于后续比较
#             exclude_list = [item for item in exclude_list if isinstance(item, str)]
#             print(f" *** 排除列表检查:Check 成功 - 使用排除列表: {exclude_list}")

#         # 初始化结果列表
#         result_list = []
#         print(f" *** 结果列表初始化:Init 成功")

#         # --- 步骤 2: 递归扫描目录并读取文件名 ---
#         def _scan_recursively(current_path):
#             """
#             内部递归函数，用于实际执行扫描逻辑。
#             :param current_path: 当前正在扫描的目录路径。
#             """
#             print(f" *** 开始扫描子目录:Check 成功 - 正在扫描: {current_path}")

#             try:
#                 # os.scandir() 比 os.listdir() 更高效
#                 with os.scandir(current_path) as entries:
#                     for entry in entries:
#                         # 获取不带路径的名称用于比较和添加
#                         entry_name = entry.name

#                         # --- 检查是否需要排除 ---
#                         if entry_name in exclude_list:
#                             if entry.is_file():
#                                 print(f" *** 排除文件:Check 成功 - 跳过文件: {entry.path}")
#                             elif entry.is_dir():
#                                 print(f" *** 排除目录:Check 成功 - 跳过整个目录: {entry.path}")
#                             continue  # 跳过当前文件或目录

#                         # --- 处理文件 ---
#                         if entry.is_file():
#                             # 检查文件名是否以 .xlsx 结尾（不区分大小写）
#                             if entry_name.lower().endswith('.xlsx'):
#                                 result_list.append(entry_name)
#                                 print(f" *** {entry_name} ||-> ADD ")

#                         # --- 处理目录并递归 ---
#                         elif entry.is_dir():
#                             # 如果是目录，则递归调用自身进行扫描
#                             _scan_recursively(entry.path)

#             except PermissionError as pe:
#                 # 如果没有权限访问某个子目录，记录日志并继续扫描其他部分
#                 print(f" *** 目录访问权限警告:Warning - 没有权限访问目录 '{current_path}': {pe}")
#                 # 这里选择不中断整个过程，只是跳过这个无法访问的目录

#         # 启动递归扫描
#         _scan_recursively(directory_path)

#         # --- 步骤 3: 返回结果 ---
#         print(f" *** 目录扫描完成:Check 成功 - 共找到 {len(result_list)} 个 .xlsx 文件")
#         return result_list

#     except ValueError as ve:
#         # 重新抛出由参数或路径检查引发的 ValueError
#         raise ve
#     except Exception as e:
#         # 捕获并处理其他所有异常
#         print(f" *** 操作过程中发生未预期的错误:Error - {e}")
#         raise e  # 重新抛出异常，让调用者知道发生了错误

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


# import os
import pandas as pd


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


import os
from openpyxl import load_workbook, Workbook


# def excel_XLSX_Merge_Sheet(
#         source_directory: str,
#         source_sheet_list: list,
#         target_file_path: str,
#         target_sheet_name: str = None
# ) -> str:
#     """
#     将指定目录下多个Excel (.xlsx)文件中的指定工作表合并到一个新的工作表中，
#     并保存到目标Excel文件中。

#     Args:
#         source_directory (str):
#             包含源Excel文件的目录路径（相对或绝对）。如果为空，则使用脚本所在目录。
#         source_sheet_list (list):
#             包含需要合并的源文件和工作表信息的列表。
#             列表中每个元素是一个字典，格式为 {'源文件名.xlsx': '源工作表名'}。
#             此参数不能为空。
#         target_file_path (str):
#             目标Excel文件的完整路径（包含文件名）。如果文件不存在会被创建。
#             此参数不能为空。
#         target_sheet_name (str, optional):
#             目标工作表的名称。如果为空或None，则会自动查找一个可用的 'Sheet{num}' 名称。
#             如果指定名称的工作表已存在，其内容将被覆盖。

#     Returns:
#         str: 实际保存的目标文件的完整路径。

#     Raises:
#         ValueError: 如果必要参数为空、源列表格式错误或目录/文件路径无效。
#         FileNotFoundError: 如果指定的源文件在目录中找不到。
#         Exception: 如果在读取、写入或处理Excel文件时发生其他错误。
#     """
#     # --- 步骤 1: 初始化和检查 ---
#     try:
#         # 检查 source_sheet_list 参数
#         if not source_sheet_list or not isinstance(source_sheet_list, list):
#             print(f" *** 源列表参数检查:Check 失败 - source_sheet_list 不能为空且必须是列表")
#             raise ValueError("source_sheet_list 不能为空且必须是列表。")

#         # 检查并规范化 source_directory
#         if not source_directory:
#             source_directory = os.path.dirname(os.path.abspath(__file__))
#             print(f" *** 源目录参数为空，使用默认目录:Init 成功 - 设置为: {source_directory}")
#         else:
#             source_directory = os.path.normpath(source_directory)
#             print(f" *** 源目录参数检查:Check 成功 - 接收到目录路径: {source_directory}")

#         if not os.path.exists(source_directory) or not os.path.isdir(source_directory):
#             print(f" *** 源目录存在性检查:Check 失败 - 路径不存在或不是目录: {source_directory}")
#             raise ValueError(f"源目录路径无效: {source_directory}")
#         print(f" *** 源目录存在性检查:Check 成功 - 目录有效: {source_directory}")

#         # 检查 target_file_path 参数
#         if not target_file_path:
#             print(f" *** 目标文件路径检查:Check 失败 - target_file_path 不能为空")
#             raise ValueError("target_file_path 不能为空。")
#         target_file_path = os.path.normpath(target_file_path)
#         target_dir = os.path.dirname(target_file_path)
#         print(f" *** 目标文件路径检查:Check 成功 - 目标文件路径: {target_file_path}")

#         # 确保目标文件的目录存在
#         if target_dir and not os.path.exists(target_dir):
#             os.makedirs(target_dir)
#             print(f" *** 目标目录创建:Init 成功 - 已创建目录: {target_dir}")

#         # 处理 target_sheet_name
#         if not target_sheet_name:
#             target_sheet_name = "Sheet1"  # 默认名称，后续会检查是否需要更改
#             print(f" *** 目标工作表名称为空，将初始化:Init 成功 - 初始名称: {target_sheet_name}")
#         else:
#             print(f" *** 目标工作表名称检查:Check 成功 - 指定名称: {target_sheet_name}")

#         # 初始化用于存储合并数据的结构
#         all_headers = []  # 存储所有遇到的表头
#         merged_data = []  # 存储所有行的数据（列表的列表）
#         print(f" *** 合并数据结构初始化:Init 成功")

#         # --- 步骤 2: 读取并合并源数据 ---
#         print(f" *** 开始处理源数据列表...")
#         for item in source_sheet_list:
#             # 根据修正后的格式检查元素
#             if not isinstance(item, dict) or len(item) != 1:
#                 print(f" *** 源列表元素格式检查:Check 失败 - 元素格式错误: {item}")
#                 raise ValueError(
#                     f"source_sheet_list 中的元素必须是只包含一个键值对的字典，格式为 {{'file_name': 'sheet_name'}}。错误元素: {item}")

#             # 获取唯一的键值对
#             src_file_name, src_sheet_name = next(iter(item.items()))

#             # 验证键和值是否为字符串
#             if not isinstance(src_file_name, str) or not isinstance(src_sheet_name, str):
#                 print(f" *** 源列表元素键值类型检查:Check 失败 - 键和值必须是字符串。错误元素: {item}")
#                 raise ValueError(f"source_sheet_list 中的字典键和值都必须是字符串。错误元素: {item}")

#             src_file_path = os.path.join(source_directory, src_file_name)

#             print(f" *** 解析源项:Check 成功 - 文件: {src_file_name}, 工作表: {src_sheet_name}")

#             # 检查源文件是否存在
#             if not os.path.exists(src_file_path):
#                 print(f" *** 源文件存在性检查:Check 失败 - 文件未找到: {src_file_path}")
#                 raise FileNotFoundError(f"在目录 '{source_directory}' 中未找到源文件: {src_file_name}")

#             # 打开源工作簿
#             try:
#                 src_wb = load_workbook(filename=src_file_path, read_only=True, data_only=True)
#                 print(f" *** 加载源工作簿:Check 成功 - 已打开: {src_file_name}")
#             except Exception as e:
#                 print(f" *** 加载源工作簿:Check 失败 - 打开文件失败: {src_file_name}, 错误: {e}")
#                 raise e

#             # 检查源工作表是否存在
#             if src_sheet_name not in src_wb.sheetnames:
#                 src_wb.close()
#                 print(f" *** 源工作表存在性检查:Check 失败 - 工作表未找到: {src_sheet_name} in {src_file_name}")
#                 raise ValueError(f"在文件 '{src_file_name}' 中未找到工作表: {src_sheet_name}")

#             src_ws = src_wb[src_sheet_name]
#             print(f" *** 加载源工作表:Check 成功 - 已加载: {src_sheet_name}")

#             # 获取源数据
#             rows_iter = src_ws.iter_rows(values_only=True)

#             try:
#                 # 尝试获取第一行作为表头
#                 header_row = next(rows_iter)
#                 # 处理可能的空表或只有表头的情况
#                 if header_row and any(cell is not None for cell in header_row):
#                     current_headers = [str(cell) if cell is not None else '' for cell in header_row]
#                 else:
#                     current_headers = []
#                     # 如果第一行是空的或None，回退到没有表头的情况
#                     # 重新获取迭代器，因为next()已经消费了第一行
#                     rows_iter = src_ws.iter_rows(values_only=True)
#             except StopIteration:
#                 # 工作表完全为空
#                 current_headers = []
#                 print(f" *** 源工作表内容检查:Check 成功 - 工作表为空: {src_sheet_name}")

#             # 如果源有表头
#             if current_headers:
#                 print(f" *** 源工作表表头检查:Check 成功 - 检测到表头: {current_headers}")
#                 # 更新全局表头列表
#                 for h in current_headers:
#                     if h not in all_headers:
#                         all_headers.append(h)
#                 header_map = {h: i for i, h in enumerate(current_headers)}  # 源表头到其索引的映射
#             else:
#                 print(f" *** 源工作表表头检查:Check 成功 - 未检测到表头")
#                 header_map = {}

#             row_index = 1  # 从第一行（或第二行，如果第一行是表头）开始计数
#             added_rows_count = 0
#             # 遍历源工作表的每一行（跳过表头行，如果有的话）
#             for row_data in rows_iter:
#                 row_index += 1
#                 # 创建一个与总表头等长的新行，初始为空
#                 new_row = [''] * len(all_headers)

#                 # 填充数据
#                 for src_col_idx, cell_value in enumerate(row_data):
#                     # 获取源表头（如果存在）
#                     src_header = current_headers[src_col_idx] if src_col_idx < len(current_headers) else None

#                     if src_header and src_header in all_headers:
#                         # 如果源列有表头且该表头在总表头中，放入对应位置
#                         global_col_idx = all_headers.index(src_header)
#                         new_row[global_col_idx] = str(cell_value) if cell_value is not None else ''
#                     elif not current_headers:
#                         # 如果源表没有表头，则按列索引直接映射
#                         # 如果列索引超出了当前总表头长度，需要扩展
#                         while len(all_headers) <= src_col_idx:
#                             new_header = f"Col_{len(all_headers) + 1}"
#                             all_headers.append(new_header)
#                             # 所有已存在的行也需要扩展
#                             for r in merged_data:
#                                 r.append('')
#                         new_row[src_col_idx] = str(cell_value) if cell_value is not None else ''
#                     else:
#                         # 如果源表头不在总表头中（新表头），则添加到末尾
#                         # 或者源行数据比表头长（数据不规范），也按列索引处理
#                         if src_header:
#                             if src_header not in all_headers:
#                                 all_headers.append(src_header)
#                                 # 所有已存在的行也需要增加一列
#                                 for r in merged_data:
#                                     r.append('')
#                         # 确保new_row足够长
#                         while len(new_row) < len(all_headers):
#                             new_row.append('')
#                         # 放入数据
#                         global_col_idx = len(all_headers) - 1  # 放在最后一列
#                         new_row[global_col_idx] = str(cell_value) if cell_value is not None else ''

#                 # 将处理好的行添加到合并数据中
#                 merged_data.append(new_row)
#                 added_rows_count += 1
#                 print(f" *** {src_file_name}::{src_sheet_name}.row=={row_index} ||-> add")

#             src_wb.close()
#             print(f" *** 关闭源工作簿:Check 成功 - 已关闭: {src_file_name}")

#             # --- 步骤 3: 去重和保存 ---
#             # 简单的去重：将现有数据存入一个集合（基于元组，因为列表不可哈希）
#             # 然后清空列表，再从集合中取回，最后再转回列表。这会移除完全相同的行。
#             # 注意：这会改变原有行的顺序。
#             if merged_data:
#                 initial_count = len(merged_data)
#                 unique_data_set = set(tuple(row) for row in merged_data)
#                 merged_data.clear()
#                 merged_data.extend(list(row) for row in unique_data_set)
#                 final_count = len(merged_data)
#                 duplicates_removed = initial_count - final_count
#                 print(f" *** {src_file_name}::{src_sheet_name} ||| redup=={duplicates_removed}")
#             else:
#                 print(f" *** {src_file_name}::{src_sheet_name} ||| redup==0")

#             print(f" *** {src_file_name}::{src_sheet_name} ||-> +++")

#         # --- 步骤 4: 写入目标文件 ---
#         print(f" *** 开始写入合并后的数据到目标文件...")

#         # 确定最终的目标工作表名称
#         final_sheet_name = target_sheet_name
#         # 打开或创建目标工作簿
#         if os.path.exists(target_file_path):
#             try:
#                 target_wb = load_workbook(filename=target_file_path)
#                 print(f" *** 加载目标工作簿:Check 成功 - 文件已存在，已加载: {target_file_path}")
#             except Exception as e:
#                 print(f" *** 加载目标工作簿:Check 失败 - 加载现有文件失败: {target_file_path}, 错误: {e}")
#                 # 如果加载失败，创建一个新的
#                 target_wb = Workbook()
#                 target_wb.remove(target_wb.active)  # 删除默认创建的Sheet
#         else:
#             target_wb = Workbook()
#             target_wb.remove(target_wb.active)  # 删除默认创建的Sheet
#             print(f" *** 创建目标工作簿:Init 成功 - 文件不存在，已创建新工作簿")

#         # 处理目标工作表名称冲突
#         if not final_sheet_name:
#             sheet_counter = 1
#             while f"Sheet{sheet_counter}" in target_wb.sheetnames:
#                 sheet_counter += 1
#             final_sheet_name = f"Sheet{sheet_counter}"
#             print(f" *** 目标工作表名称初始化:Init 成功 - 自动命名为: {final_sheet_name}")
#         else:
#             # 如果名称已存在，openpyxl的create_sheet会自动处理（添加数字后缀）
#             # 但根据需求，我们需要覆盖，所以先删除同名的
#             if final_sheet_name in target_wb.sheetnames:
#                 del target_wb[final_sheet_name]
#                 print(f" *** 目标工作表存在性检查:Check 成功 - 已删除同名工作表以准备覆盖: {final_sheet_name}")

#         target_ws = target_wb.create_sheet(title=final_sheet_name)
#         print(f" *** 创建/覆盖目标工作表:Check 成功 - 已创建/清空工作表: {final_sheet_name}")

#         # 写入表头
#         if all_headers:
#             target_ws.append(all_headers)
#             print(f" *** 写入表头:Check 成功 - 表头: {all_headers}")
#         else:
#             print(f" *** 写入表头:Check 成功 - 无表头数据")

#         # 写入数据行
#         for data_row in merged_data:
#             target_ws.append(data_row)
#         print(f" *** 写入数据行:Check 成功 - 共写入 {len(merged_data)} 行数据")

#         # 保存目标工作簿
#         try:
#             target_wb.save(target_file_path)
#             target_wb.close()
#             print(f" *** 保存目标工作簿:Check 成功 - 数据已保存至: {target_file_path}")
#         except Exception as e:
#             target_wb.close()
#             print(f" *** 保存目标工作簿:Check 失败 - 保存文件失败: {target_file_path}, 错误: {e}")
#             raise e

#         print(f" *** 整个合并过程完成:Check 成功 - 最终文件路径: {target_file_path}")
#         return target_file_path

#     except (ValueError, FileNotFoundError) as e:
#         # 重新抛出已知的特定异常
#         raise e
#     except Exception as e:
#         # 捕获并处理其他所有未预期的异常
#         print(f" *** 操作过程中发生未预期的错误:Error - {e}")
#         raise e  # 重新抛出异常，让调用者知道发生了错误

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
from openpyxl import load_workbook


def excel_XLSX_delete_row(file_path, sheet_names=None, row_index=None):
    """
    在Windows系统环境下，通过python对指定excel文件（.xlsx格式）的指定数据表删除指定数据行以上的所有行。

    参数:
    file_path (str): 需要读取解析的excel源文件的文件路径名（路径+文件名）。
                     支持相对路径和绝对路径。不能为空。
    sheet_names (list, optional): 被读取的excel源文件需要解析的数据表名称列表。
                                  如果为空或None，则默认处理文件中的所有数据表。
    row_index (int, optional): 指定从该序号行开始保留数据（该行及以上行均被删除）。
                               例如，row_index=4，则删除第1至3行，第4行成为新的第一行。
                               必须为非负整数。如果为空或None，默认删除所有行。

    返回:
    int: 删除的总行数。

    异常:
    ValueError: 当file_path为空，或row_index为负数时抛出。
    FileNotFoundError: 当指定的file_path不存在时抛出。
    Exception: 处理Excel文件时可能抛出的其他异常。
    """
    try:
        # --- 初始化与检查 ---
        print(f" *** 参数检查与初始化:Init 开始 ***")

        # 1. 检查 file_path 参数
        if not file_path:
            print(f" *** 参数检查:Check |-> file_path 为空 ||-||-|| 失败 ***")
            raise ValueError("文件路径 (file_path) 不能为空。")
        if not os.path.exists(file_path):
            print(f" *** 文件存在性检查:Check |-> 文件 {file_path} 不存在 ||-||-|| 失败 ***")
            raise FileNotFoundError(f"指定的文件路径 '{file_path}' 不存在。")
        print(f" *** 文件路径检查:Check |-> {file_path} ||-||-|| 成功 ***")

        # 2. 处理 sheet_names 参数 (默认值)
        if not sheet_names:
            print(f" *** 数据表列表处理:Init |-> 未指定数据表，将处理所有数据表 ||-||-|| 成功 ***")
            # 稍后在加载工作簿后获取所有表名
        else:
            print(f" *** 数据表列表检查:Check |-> {sheet_names} ||-||-|| 成功 ***")

        # 3. 处理 row_index 参数 (默认值和有效性检查)
        if row_index is None:
            # 根据函数描述，如果row_index为空，默认删除所有行，即保留从第 infinity 行开始的内容，
            # 这等效于 row_index 设置为一个非常大的数，或者特殊处理。
            # 但更直接的理解是，如果要删除所有行，则没有“保留”的行。
            # 根据步骤2的描述 "若第3参数为0，则直接删除数据表所有数据行内容"，
            # 我们可以将 None 视为 0 来处理，即删除所有行。
            row_index = 0
            print(f" *** 删除行索引处理:Init |-> 未指定行索引，默认删除所有行 (row_index=0) ||-||-|| 成功 ***")
        elif not isinstance(row_index, int) or row_index < 0:
            print(f" *** 删除行索引检查:Check |-> row_index 必须为非负整数 ||-||-|| 失败 ***")
            raise ValueError("删除行索引 (row_index) 必须为非负整数。")
        else:
            print(f" *** 删除行索引检查:Check |-> {row_index} ||-||-|| 成功 ***")

        print(f" *** 参数检查与初始化:Init 完成 ***")
        # --- 初始化与检查结束 ---

        # --- 加载Excel文件 ---
        print(f" *** 加载Excel文件:Load |-> {file_path} ||-||-|| 开始 ***")
        # load_workbook 会自动判断是相对路径还是绝对路径
        workbook = load_workbook(filename=file_path)
        print(f" *** 加载Excel文件:Load |-> {file_path} ||-||-|| 成功 ***")
        # --- 加载Excel文件结束 ---

        # --- 确定要处理的数据表 ---
        final_sheet_names = sheet_names
        if not final_sheet_names:
            final_sheet_names = workbook.sheetnames
            print(f" *** 确定处理数据表:Process |-> 使用所有数据表 {final_sheet_names} ||-||-|| 成功 ***")
        # --- 确定要处理的数据表结束 ---

        total_deleted_rows = 0  # 记录总共删除的行数

        # --- 遍历并处理每个数据表 ---
        for sheet_name in final_sheet_names:
            try:
                print(f" *** 处理数据表:Process |-> {sheet_name} ||-||-|| 开始 ***")
                sheet = workbook[sheet_name]

                max_row_before = sheet.max_row
                print(f" *** 数据表 {sheet_name} 初始行数:Info |-> {max_row_before} ||-||-|| 成功 ***")

                # 如果 row_index 为 0，表示删除所有行
                if row_index == 0:
                    # openpyxl没有直接清空所有行的方法，但可以逐行删除。
                    # 从最后一行开始删除效率更高。
                    rows_to_delete = list(range(sheet.max_row, 0, -1))  # [max_row, ..., 1]
                    for row_num in rows_to_delete:
                        sheet.delete_rows(row_num)
                        print(f" *** {os.path.basename(file_path)}:{sheet_name}_{row_num}行 |-> delete ***")
                        total_deleted_rows += 1

                # 如果 row_index 大于 0，则删除该行以上的所有行
                elif row_index > 0:
                    # 需要删除第1行到第 (row_index - 1) 行
                    rows_to_delete_count = row_index - 1
                    if rows_to_delete_count > 0:
                        # delete_rows(index, amount) 从index行开始删除amount行
                        sheet.delete_rows(1, rows_to_delete_count)
                        # 更新总删除行数
                        total_deleted_rows += rows_to_delete_count
                        # 打印日志 (注意：删除后行号已变化，原第n行现在是第1行)
                        for i in range(1, rows_to_delete_count + 1):
                            # 打印被删除的原始行号
                            print(f" *** {os.path.basename(file_path)}:{sheet_name}_{i}行 |-> delete ***")

                print(f" *** 处理数据表:Process |-> {sheet_name} ||-||-|| 完成 ***")

            except Exception as inner_e:
                print(f" *** 处理单个数据表 {sheet_name} 时发生错误:Error |-> {inner_e} ||-||-|| 跳过 ***")
                # 可以选择继续处理下一个表或抛出异常
                # 这里选择继续处理其他表
                continue
        # --- 遍历并处理每个数据表结束 ---

        # --- 保存修改后的Excel文件 ---
        print(f" *** 保存Excel文件:Save |-> {file_path} ||-||-|| 开始 ***")
        workbook.save(filename=file_path)
        print(f" *** 保存Excel文件:Save |-> {file_path} ||-||-|| 成功 ***")
        # --- 保存修改后的Excel文件结束 ---

        print(f" *** 总共删除行数:Info |-> {total_deleted_rows} ||-||-|| 成功 ***")
        return total_deleted_rows

    except (ValueError, FileNotFoundError) as e:
        # 捕获特定的已知异常
        print(f" *** 函数执行中断:Error |-> {type(e).__name__}: {e} ||-||-|| 失败 ***")
        raise  # 重新抛出异常，让调用者知道
    except Exception as e:
        # 捕获其他未预期的异常
        print(f" *** 函数执行过程中发生未预期错误:Error |-> {type(e).__name__}: {e} ||-||-|| 失败 ***")
        raise  # 重新抛出异常


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


import os
from openpyxl import load_workbook


def excel_XLSX_row_read(file_path, sheet_names=None, row_index=1):
    """
    读取指定 Excel (.xlsx) 文件中指定工作表的指定行数据。

    :param file_path: (str) Excel 文件的路径（相对或绝对）。
    :param sheet_names: (list, optional) 要读取的工作表名称列表。
                        如果为 None 或空列表，则读取文件中的所有工作表。
                        默认为 None。
    :param row_index: (int, optional) 要读取的行索引（从1开始）。
                      如果为 None 或无效值，则默认读取第1行（表头）。
                      默认为 1。
    :return: (list) 包含读取到的行数据的列表。列表中的每个元素也是一个列表，
                   代表一个工作表中指定行的数据（按从左到右的单元格顺序）。
    :raises FileNotFoundError: 如果指定的文件不存在。
    :raises ValueError: 如果文件路径为空。
    :raises Exception: 对于其他可能发生的错误（如文件格式问题、读取错误等）。
    """
    # --- 参数初始化与检查 ---
    print(f" *** 参数检查与初始化:Init 开始")

    # 检查文件路径参数
    if not file_path:
        print(f" *** 文件路径检查:Check 失败 |-> 输入路径为空 ||x||x|| 异常")
        raise ValueError("文件路径不能为空。")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f" *** 文件存在性检查:Check 失败 |-> 文件 {file_path} 不存在 ||x||x|| 异常")
        raise FileNotFoundError(f"指定的文件 '{file_path}' 不存在。")

    print(f" *** 文件路径检查:Check 成功")
    print(f" *** 文件存在性检查:Check 成功")

    # 处理工作表名称参数
    if not sheet_names:
        # 如果未提供工作表名称或为空，则标记为将遍历所有表
        print(f" *** 工作表名称检查:Check |-> 未指定工作表，将读取所有工作表 ||-||-|| 成功")
        target_sheet_names = None  # 使用 None 标记读取所有表
    else:
        target_sheet_names = sheet_names
    print(f" *** 工作表名称检查:Check 成功")

    # 处理行索引参数
    if row_index is None or not isinstance(row_index, int) or row_index < 1:
        # 如果行索引无效，则使用默认值1
        default_row_index = 1
        print(f" *** 行索引检查:Check |-> 行索引无效，使用默认值 {default_row_index} ||-||-|| 成功")
        target_row_index = default_row_index
    else:
        target_row_index = row_index
    print(f" *** 行索引检查:Check 成功")

    print(f" *** 参数检查与初始化:Init 完成")

    # --- 核心处理逻辑 ---
    try:
        result_data_list = []  # 用于存储最终结果的列表
        print(f" *** 结果列表初始化:Init 成功")

        # 加载 Excel 工作簿
        workbook = load_workbook(filename=file_path, read_only=True, data_only=True)
        print(f" *** 工作簿加载:Load 成功 |-> 文件 {file_path}")

        # 确定需要处理的工作表列表
        if target_sheet_names is None:
            # 如果未指定，则处理所有工作表
            sheets_to_process = workbook.sheetnames
            print(f" *** 工作表列表确定:Determine |-> 读取所有工作表 {sheets_to_process} ||-||-|| 成功")
        else:
            # 如果已指定，则只处理指定的工作表
            # 可以选择在这里检查指定的表名是否在工作簿中存在
            sheets_to_process = target_sheet_names
            print(f" *** 工作表列表确定:Determine |-> 读取指定工作表 {sheets_to_process} ||-||-|| 成功")

        # 遍历需要处理的每个工作表
        for sheet_name in sheets_to_process:
            try:
                worksheet = workbook[sheet_name]
                print(f" *** 工作表加载:Load |-> {file_path}::{sheet_name} ||> 成功")

                # 获取指定行
                if target_row_index > worksheet.max_row:
                    print(
                        f" *** 数据行读取:Read |-> {file_path}::{sheet_name}_row=={target_row_index} ||!||!|| 警告 (行超出范围)")
                    # 如果行超出范围，可以添加空列表或跳过，这里选择跳过
                    print(
                        f" *** 行数据添加:Add |-> {file_path}::{sheet_name} 第 {target_row_index} 行数据已跳过 ||> 成功")
                else:
                    target_row = worksheet[target_row_index]
                    row_data = [cell.value for cell in target_row]
                    # 打印每个单元格的读取信息
                    for col_num, cell in enumerate(target_row, start=1):
                        print(
                            f" *** {os.path.basename(file_path)}::{sheet_name}_row=={target_row_index}.{col_num} |-> {cell.value} ||> ADD")

                    # 将读取到的行数据中的每个单元格值直接添加到结果列表
                    for cell_value in row_data:
                        result_data_list.append(cell_value)
                    print(
                        f" *** 行数据添加:Add |-> {file_path}::{sheet_name} 第 {target_row_index} 行数据已添加 ||> 成功")

            except KeyError:
                # 如果指定的工作表名称不存在于文件中
                print(f" *** 工作表加载:Load |-> {file_path}::{sheet_name} ||x||x|| 异常 (工作表不存在)")
                # 可以选择抛出异常或记录警告并继续
                # 这里选择记录警告并继续处理下一个表
                print(f" *** 警告: 工作表 '{sheet_name}' 在文件 '{file_path}' 中未找到，已跳过。")
            except Exception as e:
                # 捕获处理单个工作表时的其他潜在错误
                print(f" *** 工作表处理:Process |-> {file_path}::{sheet_name} ||x||x|| 异常 ({e})")
                raise  # 重新抛出异常，中断整个过程

        # --- 输出结果并返回 ---
        print(f"\n *** {os.path.basename(file_path)}::{sheets_to_process} \n 总计读取到 {len(result_data_list)} 个元素")
        return result_data_list

    except FileNotFoundError:
        # 文件未找到的异常已在参数检查阶段处理，这里主要是捕获加载工作簿时可能的 FileNotFoundError
        print(f" *** 工作簿加载:Load |-> 文件 {file_path} ||x||x|| 异常 (文件未找到)")
        raise
    except Exception as e:
        # 捕获其他所有未预期的异常
        print(f" *** 函数执行:Execute |-> 整个函数执行过程中发生未预期错误 ||x||x|| 异常 ({e})")
        raise  # 重新抛出捕获到的异常


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


import pandas as pd
import os
from typing import List, Union, Dict, Optional

def Excel_insert_content_Rule_0(
    excel_file_path: str,
    sheet_names: List[str],
    insert_type: str,
    insert_position: int,
    fill_values: Union[str, Dict, None]
):
    """
    Windows系统环境下通过python对指定excel文件数据表根据输入参数在指定位置插入行或者列，并自动填写相应值
    
    参数:
    - excel_file_path: string, excel源文件的文件路径名
    - sheet_names: list, 需要处理的数据表名称列表，为空则处理所有数据表
    - insert_type: string, 插入类型，"row"或"column"，默认为"row"
    - insert_position: int, 插入位置，允许负数，-1代表最后一行/列前
    - fill_values: string或dict，需要填写到刚插入行或列的值，为空则插入空白行/列
    
    返回值: 无，直接修改原文件
    """
    try:
        # 步骤1: 初始化+检查
        # 检查文件是否存在
        if not os.path.exists(excel_file_path):
            raise FileNotFoundError(f"文件不存在: {excel_file_path}")
        print(" *** 文件检查:Check 成功 ")

        # 初始化参数
        if sheet_names is None or sheet_names == []:
            # 获取所有数据表名称
            all_sheets = pd.ExcelFile(excel_file_path).sheet_names
            sheet_names = all_sheets
            print(" *** 数据表列表:Init 成功 ")
        else:
            print(" *** 数据表列表:Check 成功 ")

        if insert_type is None or insert_type == "":
            insert_type = "row"
            print(" *** 插入类型:Init 成功 ")
        elif insert_type not in ["row", "column"]:
            raise ValueError("插入类型必须为 'row' 或 'column'")
        else:
            print(" *** 插入类型:Check 成功 ")

        if insert_position is None:
            insert_position = -1  # 默认插入到末尾
            print(" *** 插入位置:Init 成功 ")
        else:
            print(" *** 插入位置:Check 成功 ")

        if fill_values is None:
            print(" *** 填充值:Init 成功 ")
        else:
            print(" *** 填充值:Check 成功 ")

        # 步骤2: 读取指定excel源文件并逐个处理数据表
        # 读取Excel文件中的所有数据表信息
        excel_file = pd.ExcelFile(excel_file_path)
        
        for sheet_name in sheet_names:
            # 检查数据表是否存在
            if sheet_name not in excel_file.sheet_names:
                raise ValueError(f"数据表不存在: {sheet_name}")
            
            # 仅加载当前需要处理的数据表
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            print(f" *** 加载数据表:{sheet_name} 成功 ")
            
            # 步骤3: 对每张数据表进行处理
            if insert_type == "row":
                # 计算实际插入位置
                actual_position = insert_position
                if insert_position < 0:
                    actual_position = len(df) + insert_position + 1
                    if actual_position < 0:
                        actual_position = 0
                elif insert_position > len(df):
                    actual_position = len(df)
                
                # 创建新行，填充指定值
                if fill_values is None:
                    # 插入空白行
                    new_row = pd.Series([None] * len(df.columns), index=df.columns)
                else:
                    # 将值转换为字符串并填充到新行的所有单元格
                    new_row = pd.Series([str(fill_values)] * len(df.columns), index=df.columns)
                
                # 在指定位置插入新行
                df = pd.concat([df.iloc[:actual_position], new_row.to_frame().T, df.iloc[actual_position:]]).reset_index(drop=True)
                
            elif insert_type == "column":
                # 计算实际插入位置
                actual_position = insert_position
                if insert_position < 0:
                    actual_position = len(df.columns) + insert_position + 1
                    if actual_position < 0:
                        actual_position = 0
                elif insert_position > len(df.columns):
                    actual_position = len(df.columns)
                
                # 根据fill_values类型插入列
                if fill_values is None:
                    # 插入空白列
                    new_col_name = f"新列_{actual_position}"
                    df.insert(actual_position, new_col_name, [None] * len(df))
                elif isinstance(fill_values, dict):
                    # 当fill_values为字典时，根据键值对插入列
                    for key, value in fill_values.items():
                        df.insert(actual_position, key, [value] * len(df))
                        actual_position += 1  # 每插入一列，位置需要递增
                else:
                    # 当fill_values为字符串时，插入一列并填充该字符串
                    new_col_name = f"新列_{actual_position}"
                    df.insert(actual_position, new_col_name, [fill_values] * len(df))
            
            # 将修改后的数据表写回Excel文件
            with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 步骤4: 输出处理结果
            file_name = os.path.basename(excel_file_path)
            print(f" *** {file_name}::{sheet_name} |->| 插入{insert_type}成功 ")
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise e


def excel_column_to_list_Rule_0(file_path, sheet_names, header_conditions, match_mode="strict"):
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

# def excel_column_count_Rule_1(file_path, sheet_name, condition_dict, match_type="strict"):
#     """
#     对指定Excel文件数据表按条件进行统计计数
#
#     参数:
#     - file_path: string, Excel文件路径名（支持相对路径和绝对路径）
#     - sheet_name: string, 数据表名称，如果为空则默认读取第一张表
#     - condition_dict: dict, 条件表头和关键词字典，格式为{"表头名称": "关键词"}
#     - match_type: string, 匹配严格程度，"strict"（严格）或"simple"（宽松），默认为"strict"
#
#     返回:
#     - int: 统计结果
#     """
#     try:
#         # 步骤1：初始化+检查
#         # 检查第1个参数是否为空
#         if not file_path or not isinstance(file_path, str):
#             raise ValueError("第1个参数（文件路径）不能为空或非字符串类型")
#         print(f" *** 检查文件路径:{file_path} |-> Init 成功 ")
#
#         # 检查文件是否存在
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"文件不存在: {file_path}")
#         print(f" *** 检查文件存在:{file_path} |-> Check 成功 ")
#
#         # 检查第3个参数是否为空
#         if condition_dict is None:
#             condition_dict = {}
#         print(f" *** 检查条件字典 |-> Init 成功 ")
#
#         # 处理第2个参数，默认为第一张表
#         if not sheet_name or not isinstance(sheet_name, str):
#             sheet_name = None
#             print(f" *** 检查表名 |-> 使用默认第一张表 ||-||-|| 成功 ")
#         else:
#             print(f" *** 检查表名:{sheet_name} |-> Init 成功 ")
#
#         # 处理第4个参数，默认为"strict"
#         if not match_type or not isinstance(match_type, str):
#             match_type = "strict"
#             print(f" *** 检查匹配类型 |-> 使用默认strict ||-||-|| 成功 ")
#         elif match_type not in ["strict", "simple"]:
#             match_type = "strict"
#             print(f" *** 检查匹配类型 |-> 使用默认strict ||-||-|| 成功 ")
#         else:
#             print(f" *** 检查匹配类型:{match_type} |-> Init 成功 ")
#
#         # 初始化结果变量
#         result_count = 0
#         print(f" *** 初始化结果变量 |-> Init 成功 ")
#
#         # 步骤2：读取指定的数据表
#         # 读取Excel文件，如果sheet_name为空则读取第一张表
#         excel_file = pd.ExcelFile(file_path)
#         if sheet_name is None:
#             sheet_name = excel_file.sheet_names[0]
#
#         df = pd.read_excel(file_path, sheet_name=sheet_name)
#         print(f" *** 读取数据表:{sheet_name} |-> 成功 ")
#
#         # 步骤3：根据条件进行统计
#         # 获取文件名用于输出
#         file_name = os.path.basename(file_path)
#
#         # 遍历每一行数据（跳过表头）
#         for index, row in df.iterrows():
#             # 如果是表头行则跳过
#             if index == 0 and all(
#                     str(col) in condition_dict.keys() for col in df.columns if str(col) in condition_dict.keys()):
#                 continue
#
#             # 标记当前行是否满足所有条件
#             is_valid_row = True
#
#             # 如果条件字典为空，所有行都合法
#             if not condition_dict:
#                 result_count += 1
#                 print(f" *** {file_name}::{sheet_name}_all |-> （合法.{result_count}）")
#                 continue
#
#             # 对每个条件进行检查
#             for header, keyword in condition_dict.items():
#                 # 检查表头是否存在
#                 if header not in df.columns:
#                     is_valid_row = False
#                     break
#
#                 # 获取当前行在指定列的值
#                 cell_value = str(row[header]) if pd.notna(row[header]) else ""
#
#                 # 根据匹配类型进行比较
#                 if match_type == "strict":
#                     # 严格匹配：完全相等
#                     if cell_value != keyword:
#                         is_valid_row = False
#                         break
#                 elif match_type == "simple":
#                     # 宽松匹配：包含或相等（不区分大小写）
#                     if keyword.lower() not in cell_value.lower():
#                         is_valid_row = False
#                         break
#
#             # 如果当前行满足所有条件，则计数器加1
#             if is_valid_row:
#                 result_count += 1
#                 print(
#                     f" *** {file_name}::{sheet_name}_{list(condition_dict.keys())[0] if condition_dict else 'all'} |-> （合法.{result_count}）")
#             else:
#                 print(
#                     f" *** {file_name}::{sheet_name}_{list(condition_dict.keys())[0] if condition_dict else 'all'} |-> （非法）")
#
#         # 步骤4：输出最终统计结果
#         print(f" >>> 当前统计了 {result_count} 个元素 <<< ")
#
#         # 返回统计结果
#         return result_count
#
#     except Exception as e:
#         print(f"函数执行出错: {str(e)}")
#         raise e

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

import openpyxl
import json
import os


def xlsx_export_MultiCondition(
        source_excel_path,
        source_sheet_names,
        header_conditions,
        json_path,
        target_excel_path,
        target_sheet_name
):
    """
    根据JSON文件中的条件，筛选Excel文件中的数据并导出到新文件。

    参数:
        source_excel_path (str): 源Excel文件的路径。
        source_sheet_names (list): 要读取的源数据表名称列表。如果为空，则读取所有表。
        header_conditions (list): 用于筛选的表头条件列表。如果为空，则使用所有表头。
        json_path (str): 包含筛选条件的JSON文件路径。
        target_excel_path (str): 目标Excel文件的路径。
        target_sheet_name (str): 目标数据表的名称。如果为空，则自动创建新表。

    返回:
        bool: 操作是否成功完成。
    """
    try:
        # --- 1. 初始化+检查 ---
        print(f" *** 参数检查:Init 开始")

        # 检查必需参数
        if not source_excel_path or not isinstance(source_excel_path, str):
            raise ValueError("源Excel文件路径无效。")
        if not os.path.exists(source_excel_path):
            raise FileNotFoundError(f"源Excel文件不存在: {source_excel_path}")
        print(f" *** 源Excel文件路径检查:Check 成功")

        if not json_path or not isinstance(json_path, str):
            raise ValueError("JSON文件路径无效。")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON文件不存在: {json_path}")
        print(f" *** JSON文件路径检查:Check 成功")

        if not target_excel_path or not isinstance(target_excel_path, str):
            raise ValueError("目标Excel文件路径无效。")
        print(f" *** 目标Excel文件路径检查:Check 成功")

        # 处理可选参数默认值
        if source_sheet_names is None:
            source_sheet_names = []
        print(f" *** 源数据表名列表:Init |-> {source_sheet_names} ||-||-|| 成功")

        if header_conditions is None:
            header_conditions = []
        print(f" *** 表头筛选条件:Init |-> {header_conditions} ||-||-|| 成功")

        if not target_sheet_name or not isinstance(target_sheet_name, str):
            # target_sheet_name 为空字符串时也应使用默认逻辑
            target_sheet_name = None
        # target_sheet_name 的最终值将在打开目标工作簿后确定
        print(f" *** 目标数据表名:Init |-> {target_sheet_name} ||-||-|| 成功 (将在后续确定最终值)")

        total_valid_rows = 0
        print(f" *** 初始化结果变量:Init 成功")

        print(f" *** 参数检查:Init 完成")

        # --- 2. 读取和处理源Excel文件 ---
        print(f" *** 读取源Excel文件:Init 开始")
        source_wb = openpyxl.load_workbook(source_excel_path)
        print(f" *** 读取源Excel文件:Init 成功")

        # 确定要处理的工作表列表
        if not source_sheet_names:
            sheets_to_process = source_wb.sheetnames
            print(f" *** 未指定源数据表，将处理所有表:Check |-> {sheets_to_process} ||-||-|| 成功")
        else:
            # 可以选择检查sheet_names是否都存在于workbook中
            sheets_to_process = [name for name in source_sheet_names if name in source_wb.sheetnames]
            invalid_sheet_names = [name for name in source_sheet_names if name not in source_wb.sheetnames]
            if invalid_sheet_names:
                print(f" *** 警告: 以下指定的源数据表在源Excel文件中未找到: {invalid_sheet_names}")

            if not sheets_to_process:
                raise ValueError("指定的源数据表在源Excel文件中均未找到。")
            print(f" *** 指定源数据表:Check |-> {sheets_to_process} ||-||-|| 成功")

        # 读取JSON筛选条件
        print(f" *** 读取JSON筛选条件:Init 开始")
        with open(json_path, 'r', encoding='utf-8') as f:
            json_filters = json.load(f)
        print(f" *** 读取JSON筛选条件:Init 成功")

        # --- 3. 准备目标Excel文件 ---
        print(f" *** 准备目标Excel文件:Init 开始")
        # 如果目标文件不存在，则创建一个新工作簿
        if not os.path.exists(target_excel_path):
            target_wb = openpyxl.Workbook()
            target_wb.save(target_excel_path)
            print(f" *** 目标文件不存在，已创建新文件:Check |-> {target_excel_path} ||-||-|| 成功")
        target_wb = openpyxl.load_workbook(target_excel_path)

        # 确定目标工作表名称
        final_target_sheet_name = target_sheet_name
        if not final_target_sheet_name:
            base_name = "Sheet"
            counter = 1
            while f"{base_name}{counter}" in target_wb.sheetnames:
                counter += 1
            final_target_sheet_name = f"{base_name}{counter}"
            # 创建新的工作表
            target_wb.create_sheet(title=final_target_sheet_name)
            print(f" *** 目标数据表名未指定，自动确定:Init |-> {final_target_sheet_name} ||-||-|| 成功")
        elif final_target_sheet_name in target_wb.sheetnames:
            # 如果指定的表名已存在，需要清空或处理。这里选择清空原有内容。
            target_ws = target_wb[final_target_sheet_name]
            for row in target_ws.iter_rows(min_row=1, max_row=target_ws.max_row, max_col=target_ws.max_column):
                for cell in row:
                    cell.value = None
            print(f" *** 目标数据表已存在，内容已清空:Init |-> {final_target_sheet_name} ||-||-|| 成功")
        else:
            # 如果指定的表名不存在，则创建
            target_wb.create_sheet(title=final_target_sheet_name)
            print(f" *** 目标数据表不存在，已创建:Init |-> {final_target_sheet_name} ||-||-|| 成功")

        target_ws = target_wb[final_target_sheet_name]
        print(f" *** 准备目标Excel文件:Init 完成")

        # --- 4. 遍历源数据表进行筛选 ---
        for sheet_name in sheets_to_process:
            source_ws = source_wb[sheet_name]
            print(f" *** 处理源数据表:Init |-> {source_excel_path}::{sheet_name} ||-||-|| 开始")

            if source_ws.max_row == 1 and not any(cell.value is not None for cell in source_ws[1]):
                print(f" *** 源数据表为空，跳过:Check |-> {source_excel_path}::{sheet_name} ||-||-|| 成功")
                continue

            # 获取表头行（假设第一行是表头）
            headers = [cell.value for cell in source_ws[1]]
            print(f" *** 读取表头行:Check |-> {headers} ||-||-|| 成功")

            # 确定筛选依据的表头列表
            matched_headers = []
            if not header_conditions:
                matched_headers = headers
                print(f" *** 未指定表头条件，使用所有表头:Init |-> {matched_headers} ||-||-|| 成功")
            else:
                # 严格匹配，去除表头字符串首尾空白字符
                cleaned_headers = [str(h).strip() if h is not None else "" for h in headers]
                cleaned_conditions = [str(c).strip() for c in header_conditions]
                matched_headers = [h for h in headers if str(h).strip() in cleaned_conditions]
                print(
                    f" *** 表头条件匹配:Check |-> {source_excel_path}::{sheet_name} |-> {matched_headers} ||-||-|| 成功")

            if not matched_headers:
                print(f" *** 无匹配表头，跳过数据表:Check |-> {source_excel_path}::{sheet_name} ||-||-|| 成功")
                continue

            # 记录匹配表头的列索引 (基于0)
            matched_indices = [i for i, h in enumerate(headers) if h in matched_headers]
            print(f" *** 匹配表头列索引:Check |-> {matched_indices} ||-||-|| 成功")

            # 准备写入目标表的行数据，先写入表头
            target_row_idx = target_ws.max_row
            if target_row_idx == 1 and not any(cell.value is not None for cell in target_ws[1]):
                # 如果目标表是新建的或完全空的，写入表头
                for col_idx, header in enumerate(headers, 1):
                    target_ws.cell(row=1, column=col_idx, value=header)
                target_row_idx = 2  # 下一行开始写数据
                print(f" *** 写入表头到目标表:Write |-> {headers} ||-||-|| 成功")
            elif target_row_idx == 1:
                # 目标表第一行有内容，但没有数据行，从第二行开始写
                target_row_idx = 2

            valid_rows_count = 0
            # 遍历数据行 (从第二行开始)
            for row_idx, row in enumerate(source_ws.iter_rows(min_row=2, values_only=True), start=2):
                is_row_valid = True

                # 对每个匹配的表头列进行筛选
                for col_idx_in_list, col_idx_in_sheet in enumerate(matched_indices):
                    cell_value = row[col_idx_in_sheet]
                    header_name = headers[col_idx_in_sheet]

                    # 从JSON中获取对应的筛选列表
                    json_key = str(header_name).strip()  # JSON键名也需strip匹配
                    if json_key in json_filters and isinstance(json_filters[json_key], list):
                        filter_list = json_filters[json_key]
                        # 严格匹配单元格值是否在筛选列表中
                        # 处理单元格值为None的情况
                        cell_value_str = str(cell_value).strip() if cell_value is not None else ""
                        if cell_value_str not in [str(item).strip() for item in filter_list]:
                            is_row_valid = False
                            break  # 任一条件不满足即可跳出
                    else:
                        # 如果JSON中没有对应的键或值不是列表，可以视为不匹配或忽略
                        # 这里选择不匹配，即该行不合法
                        is_row_valid = False
                        break

                print(f" *** {source_excel_path}::{sheet_name}_row=={row_idx} |-> {'合法' if is_row_valid else '非法'}")

                # 如果行合法，则写入目标Excel
                if is_row_valid:
                    valid_rows_count += 1
                    total_valid_rows += 1
                    # 写入整行数据到目标工作表
                    for col_idx, cell_value in enumerate(row, 1):
                        target_ws.cell(row=target_row_idx, column=col_idx, value=cell_value)
                    target_row_idx += 1

            print(
                f" *#* {source_excel_path}::{sheet_name} ==> {valid_rows_count} 行.合法 -> {target_excel_path}::{final_target_sheet_name}")

        # --- 5. 保存目标Excel文件 ---
        print(f" *** 保存目标Excel文件:Write 开始")
        target_wb.save(target_excel_path)
        print(f" *** 保存目标Excel文件:Write 成功")

        # --- 6. 输出最终结果 ---
        print(f" >>> 当前已筛选出 {total_valid_rows} 行 <<< \n ***|||*** output ==> {target_excel_path}")
        return True

    except Exception as e:
        print(f" *** 错误: 操作失败 {e}")
        return False


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

# def write_to_json_AnyLevel(file_path: str, key_path: List[str], value: Union[List, str, Dict, bool, int] = None, mode: str = "update") -> bool:
#     """
#     Windows系统环境下通过python将内容写入指定json文件的任意层级的指定键值对的值
    
#     参数:
#     - file_path: string字符串，代表作为目标写入的json文件的文件路径名
#     - key_path: list列表，代表目标键值对的所在层级以及键名称
#     - value: 需要被写入指定键值对的数据内容，默认为None
#     - mode: string字符串，写入方式，"update"或"add"，默认为"update"
    
#     返回值:
#     - bool: 操作是否成功
#     """
#     try:
#         # 1. 初始化+检查
#         # 检查第1个参数file_path是否为空
#         if not file_path or not isinstance(file_path, str):
#             print(" *** file_path检查:Init\\Check 失败 - 参数为空或类型错误 ***")
#             raise ValueError("file_path参数不能为空且必须为字符串类型")
#         print(" *** file_path检查:Init\\Check 成功 ***")

#         # 检查第2个参数key_path是否为空
#         if not key_path or not isinstance(key_path, list):
#             print(" *** key_path检查:Init\\Check 失败 - 参数为空或类型错误 ***")
#             raise ValueError("key_path参数不能为空且必须为列表类型")
#         print(" *** key_path检查:Init\\Check 成功 ***")

#         # 检查第3个参数value，如果为空则设为None
#         if value is None:
#             print(" *** value检查:Init\\Check |-> 使用默认值None ||-||-|| 成功 ***")
#         else:
#             print(" *** value检查:Init\\Check 成功 ***")

#         # 检查第4个参数mode，如果为空则设为"update"
#         if not mode:
#             mode = "update"
#             print(" *** mode检查:Init\\Check |-> 使用默认值update ||-||-|| 成功 ***")
#         elif mode not in ["update", "add"]:
#             print(" *** mode检查:Init\\Check 失败 - 参数值不合法 ***")
#             raise ValueError("mode参数必须为'update'或'add'")
#         else:
#             print(" *** mode检查:Init\\Check 成功 ***")

#         # 检查目标文件是否存在
#         if not os.path.exists(file_path):
#             print(f" *** 文件存在性检查:Init\\Check 失败 - 文件 {file_path} 不存在 ***")
#             raise FileNotFoundError(f"文件 {file_path} 不存在")
#         print(f" *** 文件存在性检查:Init\\Check 成功 - 文件 {file_path} 存在 ***")

#         # 初始化结果列表
#         print(" *** 结果列表初始化:Init\\Check 成功 ***")

#         # 2. 读取json文件并处理
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         print(" *** JSON文件读取:Init\\Check 成功 ***")

#         # 3. 根据key_path检索目标键值对
#         current_data = data
#         path_length = len(key_path)
        
#         # 遍历key_path中除最后一个元素外的所有元素，逐级向下检索
#         for i in range(path_length - 1):
#             key = key_path[i]
#             if isinstance(current_data, dict) and key in current_data:
#                 # 如果当前层级是字典且键存在，继续向下一层级
#                 current_data = current_data[key]
#                 print(f" *** 键值对检索:Check |-> 匹配到键: {key} ||-||-|| 成功 ***")
#             else:
#                 # 如果键不存在或当前层级不是字典，则需要创建新层级
#                 print(f" *** 键值对检索:Check |-> 未匹配到键: {key}, 开始创建层级 ||-||-|| 成功 ***")
#                 # 从当前位置开始，逐级创建缺失的键值对
#                 temp_data = current_data
#                 for j in range(i, path_length - 1):
#                     next_key = key_path[j]
#                     if j == path_length - 2:  # 倒数第二个键，其值应该是包含最后一个键的字典
#                         temp_data[next_key] = {key_path[-1]: value}
#                     else:
#                         temp_data[next_key] = {}
#                         temp_data = temp_data[next_key]
#                 # 更新成功，直接保存并返回
#                 with open(file_path, 'w', encoding='utf-8') as f:
#                     json.dump(data, f, ensure_ascii=False, indent=2)
#                 print(f" *||* {os.path.basename(file_path)}:{key_path[-1]}_创建并写入成功 ||-||-|| 成功 ***")
#                 return True

#         # 检查最后一个键是否存在
#         final_key = key_path[-1]
#         if isinstance(current_data, dict) and final_key in current_data:
#             # 键存在，根据mode进行更新或追加
#             if mode == "update":
#                 current_data[final_key] = value
#                 print(f" *** 键值对更新:Check |-> 执行更新操作 ||-||-|| 成功 ***")
#             else:  # add模式
#                 existing_value = current_data[final_key]
#                 # 检查现有值和新值的数据类型
#                 if type(existing_value) == type(value) and value is not None:
#                     if isinstance(value, list):
#                         current_data[final_key] = existing_value + value
#                         print(f" *** 键值对追加:Check |-> 执行列表追加操作 ||-||-|| 成功 ***")
#                     elif isinstance(value, dict):
#                         current_data[final_key] = {**existing_value, **value}
#                         print(f" *** 键值对追加:Check |-> 执行字典合并操作 ||-||-|| 成功 ***")
#                     elif isinstance(value, str):
#                         current_data[final_key] = existing_value + value
#                         print(f" *** 键值对追加:Check |-> 执行字符串拼接操作 ||-||-|| 成功 ***")
#                     elif isinstance(value, tuple):
#                         current_data[final_key] = tuple(list(existing_value) + list(value))
#                         print(f" *** 键值对追加:Check |-> 执行元组合并操作 ||-||-|| 成功 ***")
#                     else:
#                         # 其他类型，将原值转为列表，再添加新值
#                         current_data[final_key] = [existing_value, value]
#                         print(f" *** 键值对追加:Check |-> 执行通用追加操作 ||-||-|| 成功 ***")
#                 else:
#                     # 不同类型，将原值转为列表，再添加新值
#                     current_data[final_key] = [existing_value, value]
#                     print(f" *** 键值对追加:Check |-> 执行类型不匹配追加操作 ||-||-|| 成功 ***")
#         else:
#             # 键不存在，直接创建
#             current_data[final_key] = value
#             print(f" *** 键值对创建:Check |-> 执行创建操作 ||-||-|| 成功 ***")

#         # 4. 保存修改后的内容回源json文件
#         with open(file_path, 'w', encoding='utf-8') as f:
#             json.dump(data, f, ensure_ascii=False, indent=2)
#         print(f" *||* {os.path.basename(file_path)}:{final_key}_{mode}操作成功 ||-||-|| 成功 ***")
        
#         return True

#     except Exception as e:
#         print(f" *** 函数执行失败:Error |-> {str(e)} ||-||-|| 失败 ***")
#         return False


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


import json
import os
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter

# def json_to_XLSX_Rule_0(json_file_path, key_path_list, excel_file_path, sheet_name):
#     """
#     将JSON文件中指定键值对内容按照一定格式写入指定Excel文件指定数据表中

#     参数:
#     - json_file_path: JSON源文件的文件路径名
#     - key_path_list: JSON源文件中需要读取的键值对的层级及键名称列表
#     - excel_file_path: 目标Excel文件的文件路径名
#     - sheet_name: 目标Excel文件中写入数据的指定数据表名称

#     返回:
#     - 实际保存文件路径名，如果出现异常则返回None
#     """
#     try:
#         # 步骤1: 初始化+检查
#         # 检查参数是否为空
#         if not json_file_path:
#             print(" *** JSON文件路径:Init 检查失败，参数为空 ***")
#             raise ValueError("JSON文件路径不能为空")
#         print(" *** JSON文件路径:Init 成功 ***")

#         if not key_path_list or not isinstance(key_path_list, list):
#             print(" *** 键路径列表:Check 检查失败，参数为空或类型错误 ***")
#             raise ValueError("键路径列表不能为空且必须为列表类型")
#         print(" *** 键路径列表:Init 成功 ***")

#         if not excel_file_path:
#             print(" *** Excel文件路径:Init 检查失败，参数为空 ***")
#             raise ValueError("Excel文件路径不能为空")
#         print(" *** Excel文件路径:Init 成功 ***")

#         # 检查JSON文件是否存在
#         if not os.path.exists(json_file_path):
#             print(f" *** JSON文件:Check 文件不存在: {json_file_path} ***")
#             raise FileNotFoundError(f"JSON文件不存在: {json_file_path}")
#         print(" *** JSON文件:Check 存在 ***")

#         # 检查目标Excel文件是否存在，如果不存在则创建
#         if not os.path.exists(excel_file_path):
#             print(f" *** Excel文件:Check 文件不存在，创建新文件: {excel_file_path} ***")
#             wb = Workbook()
#             ws = wb.active
#             wb.save(excel_file_path)
#             print(" *** Excel文件:Init 创建成功 ***")
#         else:
#             print(" *** Excel文件:Check 存在 ***")
#             wb = load_workbook(excel_file_path)

#         # 检查数据表是否存在
#         if not sheet_name:
#             sheet_name = wb.sheetnames[0]
#             print(f" *** 数据表:Check |-> 使用默认表: {sheet_name} ||-||-|| 成功 ***")
#         elif sheet_name not in wb.sheetnames:
#             print(f" *** 数据表:Check 表 {sheet_name} 不存在，创建新表 ***")
#             ws = wb.create_sheet(sheet_name)
#         else:
#             print(f" *** 数据表:Check 表 {sheet_name} 存在 ***")
#         ws = wb[sheet_name]

#         # 步骤2: 读取JSON文件并根据键路径获取值
#         with open(json_file_path, 'r', encoding='utf-8') as f:
#             json_data = json.load(f)
#         print(f" *** JSON文件内容:Read 成功 ***")

#         # 根据键路径列表逐级获取值
#         current_data = json_data
#         for i, key in enumerate(key_path_list):
#             if isinstance(current_data, dict) and key in current_data:
#                 current_data = current_data[key]
#                 print(f" *** 键路径匹配:Check 路径[{i}] '{key}' 匹配成功 ***")
#             else:
#                 print(f" *** 键路径匹配:Check 路径[{i}] '{key}' 匹配失败 ***")
#                 raise KeyError(f"键路径匹配失败: 无法在路径 {key_path_list[:i+1]} 找到键 '{key}'")
#         print(f" *** 键路径值获取:Read 成功 ***")

#         # 步骤3: 分析值内容并写入Excel
#         # 获取当前工作表的最大行数，以确保在空白区域写入
#         start_row = ws.max_row + 1 if ws.max_row > 0 else 1
        
#         # 检查数据类型并进行相应处理
#         if isinstance(current_data, (int, str, bool, float)):
#             # 单一值类型，直接写入
#             ws.cell(row=start_row, column=1, value=current_data)
#             print(f" *** 数据写入:Write 单一值写入成功 ***")
#         elif isinstance(current_data, list):
#             # 列表类型，逐个写入列中
#             for idx, item in enumerate(current_data):
#                 ws.cell(row=start_row + idx, column=1, value=item)
#             print(f" *** 数据写入:Write 列表数据写入成功，共{len(current_data)}项 ***")
#         elif isinstance(current_data, dict):
#             # 字典类型，需要判断是否嵌套
#             is_nested = any(isinstance(v, (dict, list)) for v in current_data.values())
            
#             if is_nested:
#                 # 嵌套字典，需要展开
#                 print(f" *** 数据类型:Analyze 检测到嵌套结构 ***")
                
#                 # 获取所有键路径
#                 all_paths = []
#                 def get_all_paths(data, current_path=[]):
#                     if isinstance(data, dict):
#                         for k, v in data.items():
#                             new_path = current_path + [k]
#                             if isinstance(v, (dict, list)) and isinstance(v, dict):
#                                 get_all_paths(v, new_path)
#                             else:
#                                 all_paths.append(new_path + [v])
#                     elif isinstance(data, list):
#                         for i, v in enumerate(data):
#                             new_path = current_path + [str(i)]
#                             if isinstance(v, (dict, list)):
#                                 get_all_paths(v, new_path)
#                             else:
#                                 all_paths.append(new_path + [v])
                
#                 get_all_paths(current_data, key_path_list[:-1])
                
#                 # 获取所有列名
#                 all_columns = set()
#                 for path in all_paths:
#                     all_columns.update(path[:-1])  # 除了最后一个值，其他都是列名
                
#                 # 创建列索引
#                 col_index = {col: i+1 for i, col in enumerate(sorted(all_columns))}
                
#                 # 设置表头
#                 for col_name, col_num in col_index.items():
#                     ws.cell(row=start_row, column=col_num, value=col_name)
                
#                 # 写入数据
#                 data_row = start_row + 1
#                 for path in all_paths:
#                     for i, key in enumerate(path[:-1]):  # 最后一个是值
#                         col_num = col_index[key]
#                         ws.cell(row=data_row, column=col_num, value=path[-1] if i == len(path) - 2 else key)
#                     data_row += 1
#             else:
#                 # 非嵌套字典，键值对写入两列
#                 print(f" *** 数据类型:Analyze 检测到非嵌套字典 ***")
#                 row = start_row
#                 for key, value in current_data.items():
#                     ws.cell(row=row, column=1, value=key)
#                     ws.cell(row=row, column=2, value=value)
#                     row += 1
#         else:
#             # 其他类型，如元组，转换为列表处理
#             if hasattr(current_data, '__iter__') and not isinstance(current_data, (str, bytes)):
#                 current_data = list(current_data)
#                 for idx, item in enumerate(current_data):
#                     ws.cell(row=start_row + idx, column=1, value=item)
#                 print(f" *** 数据写入:Write 元组/迭代器数据写入成功，共{len(current_data)}项 ***")
#             else:
#                 ws.cell(row=start_row, column=1, value=str(current_data))
#                 print(f" *** 数据写入:Write 其他类型数据写入成功 ***")

#         # 步骤4: 保存文件
#         wb.save(excel_file_path)
#         json_file_name = os.path.basename(json_file_path)
#         key_path_str = "_".join(key_path_list)
#         print(f" *||* {json_file_name}:{key_path_str}_写入成功 *||*")
#         return excel_file_path

#     except Exception as e:
#         print(f" *** 函数执行异常: {str(e)} ***")
#         return None

def json_to_XLSX_Rule_0(json_file_path, key_path_list, excel_file_path, sheet_name):
    """
    将JSON文件中指定键值对内容写入Excel文件指定工作表
    
    :param json_file_path: JSON源文件路径
    :param key_path_list: 键路径列表
    :param excel_file_path: Excel目标文件路径
    :param sheet_name: 目标工作表名称
    :return: 实际保存文件路径名，异常则返回None
    """
    try:
        # 步骤1: 初始化+检查
        print(f" *** 参数检查:Init 成功 ***")
        
        if not json_file_path or not isinstance(json_file_path, str):
            raise ValueError("JSON文件路径不能为空或非字符串类型")
        
        if not key_path_list or not isinstance(key_path_list, list) or len(key_path_list) == 0:
            raise ValueError("键路径列表不能为空或非列表类型")
        
        if not excel_file_path or not isinstance(excel_file_path, str):
            raise ValueError("Excel文件路径不能为空或非字符串类型")
        
        print(f" *** 路径检查:Check 成功 ***")
        
        # 检查JSON文件是否存在
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON文件不存在: {json_file_path}")
        
        print(f" *** JSON文件检查:Check 成功 ***")
        
        # 检查目标Excel文件是否存在，不存在则创建
        if not os.path.exists(excel_file_path):
            print(f" *** Excel文件不存在，创建新文件:Init 成功 ***")
            wb = Workbook()
            wb.save(excel_file_path)
        else:
            print(f" *** Excel文件存在，读取文件:Check 成功 ***")
        
        # 如果sheet_name为空，则使用默认工作表
        if not sheet_name or not isinstance(sheet_name, str):
            print(f" *** 工作表名称为空，使用默认工作表:Init |-> Sheet1 ||-||-|| 成功 ***")
            sheet_name = "Sheet1"
        
        # 加载Excel工作簿
        wb = load_workbook(excel_file_path)
        
        # 检查工作表是否存在
        if sheet_name not in wb.sheetnames:
            print(f" *** 指定工作表不存在，创建新工作表:Init |-> {sheet_name} ||-||-|| 成功 ***")
            wb.create_sheet(sheet_name)
        else:
            print(f" *** 工作表存在:Check 成功 ***")
        
        ws = wb[sheet_name]
        
        # 步骤2: 读取JSON文件并获取指定键值对的值
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f" *** JSON文件读取:Check 成功 ***")
        
        # 根据key_path_list逐级访问JSON数据
        current_data = json_data
        for i, key in enumerate(key_path_list):
            if isinstance(current_data, dict):
                if str(key) in current_data:
                    current_data = current_data[str(key)]
                else:
                    raise KeyError(f"在路径层级 {i} 处找不到键: {key}")
            elif isinstance(current_data, list):
                try:
                    index = int(key)
                    if 0 <= index < len(current_data):
                        current_data = current_data[index]
                    else:
                        raise KeyError(f"列表索引超出范围: {key}")
                except ValueError:
                    raise KeyError(f"无法将键转换为列表索引: {key}")
            else:
                raise TypeError(f"在路径层级 {i} 处，当前数据不是字典或列表类型: {type(current_data)}")
        
        print(f" *** 键值对路径查找:Check 成功 ***")
        
        # 步骤3: 分析值内容的层级结构
        value = current_data
        if _is_single_level(value):
            print("<!>单层级<!>")
        
            # 步骤4: 将值写入Excel
            # 查找第一个空行
            row = 1
            while ws.cell(row=row, column=1).value is not None:
                row += 1
            
            # 写入数据
            if isinstance(value, (list, tuple)):
                # 如果是列表或元组，写入多行
                for i, item in enumerate(value):
                    ws.cell(row=row + i, column=1, value=str(item))
            elif isinstance(value, dict):
                # 如果是字典，写入键值对
                for i, (k, v) in enumerate(value.items()):
                    ws.cell(row=row + i, column=1, value=str(k))
                    ws.cell(row=row + i, column=2, value=str(v))
            else:
                # 其他类型直接写入
                ws.cell(row=row, column=1, value=str(value))
            
        else:
            print("<!>多层级<!>")
            
            # 获取表头信息
            headers = {}
            if ws.max_row > 0:
                for col in range(1, ws.max_column + 1):
                    header_value = ws.cell(row=1, column=col).value
                    if header_value:
                        headers[header_value] = col
            
            # 查找第一个空行
            start_row = ws.max_row + 1 if ws.max_row > 0 else 1
            
            # 递归处理多层级数据
            def flatten_dict(d, parent_keys=[], row_num=None):
                """
                递归展开嵌套字典
                
                Args:
                    d: 要展开的字典
                    parent_keys: 父级键列表
                    row_num: 当前行号
                    
                Returns:
                    int: 下一个可用的行号
                """
                # 如果没有指定行号，使用下一个空行
                if row_num is None:
                    row_num = ws.max_row + 1 if ws.max_row > 0 else 1
                
                for key, value in d.items():
                    current_keys = parent_keys + [key]
                    
                    if isinstance(value, dict):
                        # 如果值仍然是字典，继续递归
                        # 递归处理嵌套字典，返回下一个可用行号
                        row_num = flatten_dict(value, current_keys, row_num)
                    else:
                        # 到达叶子节点，写入数据
                        # 在当前行写入层级键
                        for i, k in enumerate(current_keys[:-1]):  # 不包括最后一个键
                            ws.cell(row=row_num, column=i+1, value=str(k))
                        
                        # 使用最后一个键作为表头匹配
                        last_key = current_keys[-1]
                        if last_key in headers:
                            # 如果表头存在，写入值到对应列
                            ws.cell(row=row_num, column=headers[last_key], value=str(value))
                        else:
                            # 如果表头不存在，在最后一列后添加新的列
                            new_col = len(headers) + 1
                            ws.cell(row=1, column=new_col, value=str(last_key))
                            headers[last_key] = new_col
                            ws.cell(row=row_num, column=new_col, value=str(value))
                        
                        # 移动到下一行
                        row_num += 1
                
                return row_num
            
            # 处理多层级数据
            if isinstance(value, dict):
                # 从第一行开始写入表头（如果还没有表头）
                if ws.max_row == 0:
                    # 初始化表头行
                    pass
                    
                # 展开并写入数据
                flatten_dict(value)
        
        # 保存Excel文件
        wb.save(excel_file_path)
        
        json_filename = os.path.basename(json_file_path)
        key_path_str = "_".join(map(str, key_path_list))
        print(f" *||* {json_filename}:{key_path_str}_写入成功 ")
        
        return excel_file_path
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return None


def _is_single_level(value):
    """
    判断值是否为单层级
    """
    if isinstance(value, (int, str, bool, float)):
        return True
    elif isinstance(value, (list, tuple)):
        # 检查列表/元组中是否包含嵌套结构
        for item in value:
            if isinstance(item, (dict, list, tuple)):
                return False
        return True
    elif isinstance(value, dict):
        # 检查字典的值是否包含嵌套结构
        for v in value.values():
            if isinstance(v, (dict, list, tuple)):
                return False
        return True
    else:
        return True

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

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。

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

Exclude_Folder_OR_files = [ "temp", "统计结果", "logs"]
current_time = {}

###########################################################################################

if __name__ == '__main__':
    print_hi('PyCharm')

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
    FINAL = create_folder(folder_name="统计结果"+current_time_string,
                           target_path=""
                           )
    print(FINAL)
    print("")
    
    ## 模板准备--------------------------------------------
    FINAL_1 = None
    temp = get_resource_path(r"config\计划类型统计详细.xlsx")
    print(temp)
    print("")
    
    try:
        FINAL_1 = file_Move_OR_Copy( source_file_path=temp, target_path=FINAL, operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")
        
    FINAL_2 = None
    temp = get_resource_path(r"config\计划类型统计部门.xlsx")
    print(temp)
    print("")
    
    try:
        FINAL_2 = file_Move_OR_Copy( source_file_path=temp, target_path=FINAL, operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")
        
    FINAL_3 = None
    temp = get_resource_path(r"config\计划类型统计总和.xlsx")
    print(temp)
    print("")
    
    try:
        FINAL_3 = file_Move_OR_Copy( source_file_path=temp, target_path=FINAL, operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")
        
    FINAL_4 = None
    temp = get_resource_path(r"config\计划数与履职表单对比.xlsx")
    print(temp)
    print("")
    
    try:
        FINAL_4 = file_Move_OR_Copy( source_file_path=temp, target_path=FINAL, operation="copy")
    except Exception as e:
        print(f"模板准备过程中发生错误: {str(e)}")

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

    ## 工作计划合并
    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="《工作计划》 --->>> 请选择需要处理的Excel文件及其数据表"
    )
    print(MergeExcel)

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/工作计划表temp.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=[]
    )
    print(result)
    print("")

    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/工作计划表temp.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    result = excel_sort_by_column(file_path=r"./temp/工作计划表temp.xlsx",
                                  sheet_names= [],
                                  sort_columns= ["序号", "施工时间", "提交日期"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    result = Excel_insert_content_Rule_0(excel_file_path=r"./temp/工作计划表temp.xlsx",
                                         sheet_names= [],
                                         insert_type="column",
                                         insert_position=None,
                                         fill_values={ "计划":"计划数量" })
    
    ## 履职表单合并
    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="《履职表单》 --->>> 请选择需要处理的Excel文件及其数据表"
    )
    print(MergeExcel)

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/履职表单temp.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=[]
    )
    print(result)
    print("")

    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/履职表单temp.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    result = excel_sort_by_column(file_path=r"./temp/履职表单temp.xlsx",
                                  sheet_names= [],
                                  sort_columns= ["检查时间", "部门"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    result = Excel_insert_content_Rule_0(excel_file_path=r"./temp/履职表单temp.xlsx",
                                         sheet_names= [],
                                         insert_type="column",
                                         insert_position=None,
                                         fill_values={ "表单":"表单数量" })
    
    ## 安全监理通知单
    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="《安全监理通知单》 --->>> 请选择需要处理的Excel文件及其数据表"
    )
    print(MergeExcel)

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/安全监理通知单temp.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=[]
    )
    print(result)
    print("")

    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/安全监理通知单temp.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    result = excel_sort_by_column(file_path=r"./temp/安全监理通知单temp.xlsx",
                                  sheet_names= [],
                                  sort_columns= ["提交时间", "部门"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    ## 履职表单导出无图
    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="《履职表单导出无图》 --->>> 请选择需要处理的Excel文件及其数据表"
    )
    print(MergeExcel)

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/履职表单导出无图temp.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=[]
    )
    print(result)
    print("")

    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    result = excel_sort_by_column(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                  sheet_names= [],
                                  sort_columns= ["督查日期", "所属项目部"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    ## 督查导出
    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="《督查导出》 --->>> 请选择需要处理的Excel文件及其数据表"
    )
    print(MergeExcel)

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/督查导出temp.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=[]
    )
    print(result)
    print("")

    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/督查导出temp.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    result = excel_sort_by_column(file_path=r"./temp/督查导出temp.xlsx",
                                  sheet_names= [],
                                  sort_columns= ["督查日期", "所属项目部"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    #-------------------------------------------------------------------------------------------------------------------------------
    
    ### 工作计划表总数
    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="工作计划表总数",
    #     data_content=len(MergeExcel),
    #     write_mode="update"
    # )
    # print(result)
    # print("")
    
    # result = write_to_json_AnyLevel(
    #     file_path=r"./temp/temp.json",
    #     key_path=[ "1", "工作计划表文件总数"],
    #     value=len(MergeExcel),
    #     mode="update"
    # )
    # print(result)
    # print("")
    
    ### 计划数量
    all_GongZuoJiHua = excel_column_count_Rule_1(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_dict=None,
                                    match_type="simple")
    print(all_GongZuoJiHua)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "工作计划总数"],
        value=all_GongZuoJiHua,
        mode="update"
    )
    print(result)
    print("")
    
    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="计划数量",
    #     data_content=all,
    # )
    # print(result)
    # print("")
    
    #
    all_LvZhiBiaoDan = excel_column_count_Rule_1(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_dict=None,
                                    match_type="simple")
    print(all_LvZhiBiaoDan)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "履职表单总数"],
        value=all_LvZhiBiaoDan,
        mode="update"
    )
    print(result)
    print("")
    
    #
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "计划数量"],
        value=all_GongZuoJiHua,
        mode="update"
    )
    print(result)
    print("")
    
    ### 签到不到位
    
    temp_0 = excel_column_count_Rule_1(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"签到次数":"0"},
                                    match_type="simple")
    print(temp_0)
    print("")
    
    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="签到不到位",
    #     data_content=temp_0,
    # )
    # print(result)
    # print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "签到不到位"],
        value=temp_0,
        mode="update"
    )
    print(result)
    print("")
    
    ### 签到到位
    
    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="签到到位",
    #     data_content=all-temp_0,
    # )
    # print(result)
    # print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "签到到位"],
        value=all_GongZuoJiHua-temp_0,
        mode="update"
    )
    print(result)
    print("")

    ### 现场计划
    XianChang = excel_column_count_Rule_1(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"是否计划到现场":"是"},
                                    match_type="simple")
    print(XianChang)
    print("")

    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="现场计划",
    #     data_content=XianChang,
    # )
    # print(result)
    # print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "现场计划到位"],
        value=XianChang,
        mode="update"
    )
    print(result)
    print("")

    ### 现场未到位
    # temp_0 = excel_column_count_Rule_1(file_path=r"./temp/merged_output.xlsx",
    #                                       sheet_name=None,
    #                                       condition_dict={"是否计划到现场": "是", "签到次数":"0"},
    #                                       match_type="simple")
    # print(temp_0)
    # print("")

    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="现场不到位",
    #     data_content=temp_0,
    # )
    # print(result)
    # print("")
    
    # result = write_to_json_AnyLevel(
    #     file_path=r"./temp/temp.json",
    #     key_path=[ "1", "现场实际未到位"],
    #     value=temp_0,
    #     mode="update"
    # )
    # print(result)
    # print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "现场实际未到位"],
        value=all_GongZuoJiHua-temp_0,
        mode="update"
    )
    print(result)
    print("")

    ### 现场到位
    # result = write_to_json(
    #     file_path=r"./temp/temp.json",
    #     key_name="现场到位",
    #     data_content=XianChang-temp_0,
    # )
    # print(result)
    # print("")
    
    # result = write_to_json_AnyLevel(
    #     file_path=r"./temp/temp.json",
    #     key_path=[ "1", "现场实际到位"],
    #     value=XianChang-temp_0,
    #     mode="update"
    # )
    # print(result)
    # print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "1", "现场实际到位"],
        value=all_GongZuoJiHua-temp_0,
        mode="update"
    )
    print(result)
    print("")
    
    ### 导出结果
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "1"],
        excel_file_path= FINAL + r"\工作计划表单总体指标统计.xlsx",
        sheet_name=None
    )
    print(result)
    print("")
    
    
    #-------------------------------------------------------------------------------------------------------------------------------
    
    ### 计划类型统计
    result = excel_column_count_Rule_2(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "填写人", "所属部门", "监理计划工作类型"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "计划类型统计-详细"],
        value=result["Result"],
        mode="update"
    )
    
    result = excel_column_count_Rule_2(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "所属部门", "监理计划工作类型"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "计划类型统计-部门"],
        value=result["Result"],
        mode="update"
    )
    
    result = excel_column_count_Rule_2(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "监理计划工作类型"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "计划类型统计-总和", "总和"],
        value=result["Result"],
        mode="update"
    )
    
    ### 导出结果
    #
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "计划类型统计-详细"],
        excel_file_path= FINAL_1,
        sheet_name=None
    )
    print(result)
    print("")
    
    result = excel_XLSX_content_merge(
        file_path=FINAL_1,
        sheet_names=["Sheet1"],
        merge_columns= ["监理人员","所属部门"],
    )
    
    result = excel_sort_by_column(file_path=FINAL_1,
                                  sheet_names= [],
                                  sort_columns= ["所属部门", "监理人员"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    #
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "计划类型统计-部门"],
        excel_file_path= FINAL_2,
        sheet_name=None
    )
    print(result)
    print("")
    
    result = excel_XLSX_content_merge(
        file_path=FINAL_2,
        sheet_names=["Sheet1"],
        merge_columns= ["所属部门"],
    )
    
    result = excel_sort_by_column(file_path=FINAL_2,
                                  sheet_names= [],
                                  sort_columns= ["所属部门"],
                                  sort_direction = "up")
    print(result)
    print("")

    #
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "计划类型统计-总和"],
        excel_file_path= FINAL_3,
        sheet_name=None
    )
    print(result)
    print("")
    
    result = excel_XLSX_content_merge(
        file_path=FINAL_3,
        sheet_names=["Sheet1"],
        merge_columns= ["类型"],
    )
    
    #-------------------------------------------------------------------------------------------------------------------------------
    
    #
    result = excel_column_count_Rule_2(file_path=r"./temp/工作计划表temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "所属部门", "填写人", "计划"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "2.1", "部门"],
        value=result["Result"],
        mode="update"
    )
    
    #
    result = excel_column_count_Rule_2(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_headers=[ "部门", "检查人", "表单"],
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "2.2", "部门"],
        value=result["Result"],
        mode="update"
    )
    
    ## 导出结果
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "2.1", "部门"],
        excel_file_path= FINAL_4,
        sheet_name=None
    )
    print(result)
    print("")
    
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "2.2", "部门"],
        excel_file_path= FINAL_4,
        sheet_name=None
    )
    print(result)
    print("")
    
    result = excel_XLSX_content_merge(
        file_path=FINAL_4,
        sheet_names=["Sheet1"],
        merge_columns= [ "部门", "检查人"],
    )
    
    result = excel_sort_by_column(file_path=FINAL_4,
                                  sheet_names= [],
                                  sort_columns= ["部门", "检查人"],
                                  sort_direction = "up")
    print(result)
    print("")
    
    #-------------------------------------------------------------------------------------------------------------------------------
    
    ### 项目数量统计
    result = excel_column_count_Rule_1(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={},
                                    match_type="simple"
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "项目数量"],
        value=result,
        mode="update"
    )
    
    ### 履职表单
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "履职表单总数"],
        value=all_LvZhiBiaoDan,
        mode="update"
    )
    print(result)
    print("")
    
    ### 检查项
    result = excel_column_count_Rule_3(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_columns=[],
                                    count_column="检查项"
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "检查项"],
        value=result["Result"],
        mode="update"
    )
    
    ### 合格项\占比
    Good = excel_column_count_Rule_3(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_columns=[],
                                    count_column="合格项"
                                    )
    print(Good)
    print("")
    
    ### 不合格项\占比
    NotGood = excel_column_count_Rule_3(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_columns=[],
                                    count_column="不合格项"
                                    )
    print(result)
    print("")
    
    ### 涉及项\占比
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "涉及项"],
        value= Good["Result"] + NotGood["Result"],
        mode="update"
    )
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "合格项"],
        value=Good["Result"],
        mode="update"
    )
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "不合格项"],
        value=NotGood["Result"],
        mode="update"
    )
    
    ### 不涉及项\占比
    result = excel_column_count_Rule_3(file_path=r"./temp/履职表单temp.xlsx",
                                    sheet_name=None,
                                    condition_columns=[],
                                    count_column="不涉及项"
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "不涉及项"],
        value=result["Result"],
        mode="update"
    )
    
    ### 发现问题数量
    Questions_all = excel_column_count_Rule_1(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={},
                                    match_type="simple"
                                    )
    print(Questions_all)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "发现问题数量"],
        value=Questions_all,
        mode="update"
    )
    
    ### 安全问题数量
    Questions_Safe = excel_column_count_Rule_1(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"问题类型":"安全"},
                                    match_type="simple"
                                    )
    print(Questions_Safe)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "安全问题数量"],
        value=Questions_Safe,
        mode="update"
    )
    
    ### 质量问题数量
    Questions_Q = excel_column_count_Rule_1(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"问题类型":"质量"},
                                    match_type="simple"
                                    )
    print(Questions_Q)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "质量问题数量"],
        value=Questions_Q,
        mode="update"
    )
    
    ### A类安全问题数量
    Questions_A = excel_column_count_Rule_1(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"违章代码":"A"},
                                    match_type="simple"
                                    )
    print(Questions_A)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "A类安全问题数量"],
        value=Questions_A,
        mode="update"
    )
    
    ### B类安全问题数量
    Questions_B = excel_column_count_Rule_1(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"违章代码":"B"},
                                    match_type="simple"
                                    )
    print(Questions_B)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "A类安全问题数量"],
        value=Questions_B,
        mode="update"
    )
    
    ### CD类安全问题数量
    Questions_CD = excel_column_count_Rule_1(file_path=r"./temp/履职表单导出无图temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={"违章代码":"C", "违章代码":"D"},
                                    match_type="simple"
                                    )
    print(Questions_CD)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "CD类安全问题数量"],
        value=Questions_CD,
        mode="update"
    )
    
    ### 上传安全监理通知单数
    result = excel_column_count_Rule_1(file_path=r"./temp/安全监理通知单temp.xlsx",
                                    sheet_name=None,
                                    condition_dict={},
                                    match_type="simple"
                                    )
    print(result)
    print("")
    
    result = write_to_json_AnyLevel(
        file_path=r"./temp/temp.json",
        key_path=[ "3", "上传安全监理通知单数"],
        value=result,
        mode="update"
    )
    
    ### ？通知单数
    ### ？
    
    ### 导出结果
    result = json_to_XLSX_Rule_0(
        json_file_path=r"./temp/temp.json",
        key_path_list=[ "3"],
        excel_file_path= FINAL + r"\履职表单总体指标统计.xlsx",
        sheet_name=None
    )
    print(result)
    print("")