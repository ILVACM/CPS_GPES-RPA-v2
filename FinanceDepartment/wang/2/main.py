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

import os

def excel_Scan_XLSX(directory_path: str = None, exclude_list: list = None) -> list:
    """
    扫描指定目录及其子目录下所有 .xlsx 格式的 Excel 文件，并返回文件名列表。
    支持通过排除列表忽略特定的文件或文件夹。

    此函数会递归遍历给定目录（或默认的当前脚本目录），
    查找所有以 .xlsx 结尾的文件。在遍历过程中，如果遇到的
    文件名或文件夹名在 exclude_list 中，则会跳过该文件或整个文件夹。
    最终将所有找到的 .xlsx 文件的文件名（不包含路径）添加到列表中返回。

    Args:
        directory_path (str, optional):
            需要扫描的目录路径（相对路径或绝对路径）。
            如果未提供或为空字符串，则默认使用当前脚本所在的目录。
        exclude_list (list, optional):
            一个包含需要排除的文件名或文件夹名的列表。
            在扫描过程中，如果遇到同名的文件或文件夹，将会被忽略。
            如果未提供或为空，则不进行任何排除，递归扫描所有内容。

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
                        if entry_name in exclude_list:
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
            #}
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
        raise e # 重新抛出异常，让调用者知道发生了错误

from UI.GUI import excel_head_row_GUI_select
###

from UI.GUI import GUI_JSON_list_selector
###

from UI.GUI import GUI_XLSX_export_MultiCondition
###

from UI.GUI import GUI_XLSX_export_MultiCondition_MultiSort
###

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


        total_deleted_rows = 0 # 记录总共删除的行数

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
                    rows_to_delete = list(range(sheet.max_row, 0, -1)) # [max_row, ..., 1]
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
        raise # 重新抛出异常，让调用者知道
    except Exception as e:
        # 捕获其他未预期的异常
        print(f" *** 函数执行过程中发生未预期错误:Error |-> {type(e).__name__}: {e} ||-||-|| 失败 ***")
        raise # 重新抛出异常


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
                    print(f" *** 数据行读取:Read |-> {file_path}::{sheet_name}_row=={target_row_index} ||!||!|| 警告 (行超出范围)")
                    # 如果行超出范围，可以添加空列表或跳过，这里选择跳过
                    print(f" *** 行数据添加:Add |-> {file_path}::{sheet_name} 第 {target_row_index} 行数据已跳过 ||> 成功")
                else:
                    target_row = worksheet[target_row_index]
                    row_data = [cell.value for cell in target_row]
                    # 打印每个单元格的读取信息
                    for col_num, cell in enumerate(target_row, start=1):
                         print(f" *** {os.path.basename(file_path)}::{sheet_name}_row=={target_row_index}.{col_num} |-> {cell.value} ||> ADD")

                    # 将读取到的行数据中的每个单元格值直接添加到结果列表
                    for cell_value in row_data:
                        result_data_list.append(cell_value)
                    print(f" *** 行数据添加:Add |-> {file_path}::{sheet_name} 第 {target_row_index} 行数据已添加 ||> 成功")

            except KeyError:
                # 如果指定的工作表名称不存在于文件中
                print(f" *** 工作表加载:Load |-> {file_path}::{sheet_name} ||x||x|| 异常 (工作表不存在)")
                # 可以选择抛出异常或记录警告并继续
                # 这里选择记录警告并继续处理下一个表
                print(f" *** 警告: 工作表 '{sheet_name}' 在文件 '{file_path}' 中未找到，已跳过。")
            except Exception as e:
                # 捕获处理单个工作表时的其他潜在错误
                print(f" *** 工作表处理:Process |-> {file_path}::{sheet_name} ||x||x|| 异常 ({e})")
                raise # 重新抛出异常，中断整个过程

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
        raise # 重新抛出捕获到的异常

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
                print(f" *** 表头条件匹配:Check |-> {source_excel_path}::{sheet_name} |-> {matched_headers} ||-||-|| 成功")

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
                target_row_idx = 2 # 下一行开始写数据
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
                    json_key = str(header_name).strip() # JSON键名也需strip匹配
                    if json_key in json_filters and isinstance(json_filters[json_key], list):
                        filter_list = json_filters[json_key]
                        # 严格匹配单元格值是否在筛选列表中
                        # 处理单元格值为None的情况
                        cell_value_str = str(cell_value).strip() if cell_value is not None else ""
                        if cell_value_str not in [str(item).strip() for item in filter_list]:
                            is_row_valid = False
                            break # 任一条件不满足即可跳出
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

            print(f" *#* {source_excel_path}::{sheet_name} ==> {valid_rows_count} 行.合法 -> {target_excel_path}::{final_target_sheet_name}")


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


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。

###########################################################################################

Exclude_Folder_OR_files = ["temp"]
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

    # 临时文件夹
    result = create_folder(folder_name="temp",
                            target_path=""
                            )
    print(result)
    print("")

    result = JSON_CleanUP(file_path=r"./temp/temp.json")
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
    print("")

    for file in SourceExcel:
        temp_0 = excel_XLSX_Read_sheets(file_path= file)
        print(temp_0)
        print("")

        write_to_json(file_path=r"./temp/temp.json",
                      key_name="SourceFile",
                      data_content=temp_0,
                      write_mode="add"
                      )

    MergeExcel = GUI_JSON_list_selector(
        json_file_path=r"./temp/temp.json",
        key_name="SourceFile",
        window_title="请选择要处理的Excel文件和数据表"
    )
    print(MergeExcel)

    result = write_to_json(
        file_path=r"./temp/temp.json",
        key_name="MergeExcel",
        data_content=MergeExcel,
        write_mode="update"
    )
    print(result)
    print("")
    
    # for item in MergeExcel:
    #     pass
          
    #     for file, sheet in item.items():
    #         pass
        
    #         temp_0 = excel_head_row_GUI_select(file_path=file, 
    #                                         sheet_name=sheet)
    #         print(temp_0)
    #         print("")
            
    #         temp_0 = excel_XLSX_delete_row(file_path=file, 
    #                                     sheet_names=sheet,
    #                                     row_index=temp_0
    #                                     )
    #         print(temp_0)
    #         print("")

    result = excel_XLSX_Merge_Sheet(
        source_directory=r"./",
        source_sheet_list=MergeExcel,
        target_file_path=r"./temp/merged_output.xlsx",
        target_sheet_name="Sheet1",
        sort_columns=["凭证编号"]
    )
    print(result)
    print("")
    
    result = excel_XLSX_blank_AutoDelete(file_path=r"./temp/merged_output.xlsx",
                                         sheet_names=[]
                                         )
    print(result)
    print("")

    
    # result_path = GUI_XLSX_export_MultiCondition(
    #     src_file_path=r"temp\merged_output.xlsx",
    #     src_sheet_names=[],
    #     header_conditions=[],
    #     dst_file_path=r"./筛选导出结果.xlsx",
    #     dst_sheet_name=""
    #     )
    # if result_path:
    #     print(f"筛选完成，结果已保存至: {result_path}")
    # else:
    #     print("操作被取消或发生错误。")
    # print("")
    
    # 示例参数
    input_path = r"temp\merged_output.xlsx"
    source_sheet = r"Sheet1" # 或者 None
    headers = [] # 或者 None
    group_headers = [ "凭证编号", "凭证日期"] # 或者 []
    sort_headers = [ "会计期间", "科目编号", "一级科目编号"] # 或者 []
    output_path = r"查询结果导出.xlsx"
    output_sheet = None # 或者 None

    result_path = GUI_XLSX_export_MultiCondition_MultiSort(
        input_path, source_sheet, headers,
        group_headers, sort_headers,
        output_path, output_sheet
    )
    if result_path:
        print(f"操作成功，文件已保存至: {result_path}")
    else:
        print("操作被取消或失败。")

    # 示例参数 (请根据实际情况修改路径和文件名)
    # source_fp = r"temp\merged_output.xlsx"   # 替换为你的源文件路径
    # source_sn = ""                      # 留空则使用第一个sheet
    # filter_hl = []                      # 留空则使用所有表头
    # group_hl = [ "凭证编号", "凭证日期"]     # 根据你的数据调整
    # sort_hl = ["会计期间"]                  # 根据你的数据调整
    # target_fp = "筛选结果导出.xlsx" # 替换为你的目标文件路径
    # target_sn = ""                      # 留空则自动命名Sheet
        
    # result_path = GUI_XLSX_export_MultiCondition_MultiSort_RULE_0(
    #     source_fp, source_sn, filter_hl, group_hl, sort_hl, target_fp, target_sn
    # )
    
    # if result_path:
    #     print(f"成功导出到: {result_path}")
    # else:
    #     print("操作未完成或已取消。")