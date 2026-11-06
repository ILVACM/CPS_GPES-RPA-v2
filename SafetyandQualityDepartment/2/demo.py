import pandas as pd
import openpyxl
import os
import win32com.client as win32
import pythoncom
import datetime
import re
import shutil
from datetime import datetime

from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter  # 列索引转列字母
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from typing import Union
from collections import defaultdict

def convert_xls_to_xlsx(src_path):
    # 新增COM库初始化
    pythoncom.CoInitialize()

    # 转换为绝对路径并规范化
    src_path = os.path.abspath(src_path)
    src_path = os.path.normpath(src_path)

    # 检查文件是否存在
    if not os.path.exists(src_path):
        print(f"错误：文件不存在 - {src_path}")
        pythoncom.CoUninitialize()  # 新增：反初始化
        return None

    excel = None
    wb = None
    try:
        # 修改点1：使用Dispatch替代gencache
        excel = win32.Dispatch('Excel.Application')
        excel.Visible = False
        excel.DisplayAlerts = False  # 新增：禁用警告弹窗

        # 打开工作簿
        wb = excel.Workbooks.Open(src_path)

        # 构造新路径（将.xls替换为.xlsx）
        base, ext = os.path.splitext(src_path)
        new_path = f"{base}.xlsx"

        # 改进点：更安全的文件存在检查
        if os.path.exists(new_path):
            # 新增：可选择修改为时间戳后缀
            # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_path = f"{base}_{timestamp}.xlsx"
            print(f"提示：目标文件已存在，已自动添加时间戳后缀")

        # 保存为新格式
        wb.SaveAs(new_path, FileFormat=51)  # 51 = xlsx
        print(f"转换成功：{new_path}")
        return new_path

    except Exception as e:
        print(f"转换失败：{str(e)}")
        return None
    finally:
        # 改进点：增强资源释放
        try:
            if wb is not None:
                wb.Close(SaveChanges=False)
            if excel is not None:
                excel.Application.Quit()
                # 新增：强制释放COM对象
                del wb
                del excel
        except:
            pass

        # 新增：彻底终止Excel进程
        os.system('taskkill /IM EXCEL.EXE /F 2>NUL')
        pythoncom.CoUninitialize()  # 必须的COM库反初始化

def get_file_paths( ext="xlsx"):
    """
    获取当前目录下所有指定后缀文件的绝对路径，并返回列表。

    参数：
        ext (str): 指定的文件后缀，例如 'xlsx' 或 '.xlsx'

    返回：
        list: 包含所有匹配文件绝对路径的列表，出错时返回空列表。
    """
    file_list = []
    try:
        # 处理后缀参数，确保格式统一
        ext = ext.strip().lower()
        if not ext.startswith('.'):
            ext = '.' + ext

        # 获取当前工作目录
        current_dir = os.getcwd()

        # 遍历目录下的所有条目
        for filename in os.listdir(current_dir):
            file_path = os.path.join(current_dir, filename)

            try:
                # 检查是否为文件且后缀匹配
                if os.path.isfile(file_path) and filename.lower().endswith(ext):
                    file_list.append(file_path)
            except PermissionError:
                print(f"权限不足，无法访问文件: {filename}")
            except OSError as e:
                print(f"处理文件 {filename} 时发生系统错误: {e}")

        return file_list

    except Exception as e:
        print(f"发生全局错误: {e}")
        return file_list

def copy_and_rename_file(src_path, dest_dir, new_name):
    """
    将源文件复制到目标目录，并可选地重命名。

    参数:
        src_path (str): 源文件路径，支持相对或绝对路径。
        dest_dir (str): 目标目录路径，支持相对或绝对路径。
        new_name (str): 新文件名（可选），留空则保留原文件名。

    返回:
        bool: 操作是否成功。
    """
    try:
        # 转换为绝对路径
        src_path_abs = os.path.abspath(src_path)
        dest_dir_abs = os.path.abspath(dest_dir)

        # 获取目标文件名
        if not new_name:
            new_filename = os.path.basename(src_path_abs)
        else:
            new_filename = new_name

        # 构造目标文件路径
        dest_file_path = os.path.join(dest_dir_abs, new_filename)

        # 创建目标文件所在的目录（包括子目录）
        dest_file_dir = os.path.dirname(dest_file_path)
        os.makedirs(dest_file_dir, exist_ok=True)

        # 执行文件复制
        shutil.copy(src_path_abs, dest_file_path)

        return True
    except:
        # 捕获所有异常，返回失败状态
        return False

def is_keyword_in_filename(file_path, keyword):
    """
    判断关键词是否包含于文件名中（区分大小写）。

    参数:
        file_path (str): 包含文件名的完整路径（支持相对路径和绝对路径）。
        keyword (str): 用于匹配的关键词。

    返回:
        bool: 如果关键词是文件名的子字符串，返回 True；否则返回 False。
    """
    try:
        # 参数类型检查
        if not isinstance(file_path, str) or not isinstance(keyword, str):
            return False

        # 提取文件名部分
        filename = os.path.basename(file_path)

        # 判断关键词是否为文件名的子字符串
        return keyword in filename

    except:
        # 捕获所有异常并返回失败状态
        return False

def get_formatted_date():
    """
    获取当前系统时间中的年月日，并格式化为 'YYYY-MM-DD' 字符串。

    返回:
        str: 格式为 'YYYY-MM-DD' 的日期字符串，若出现异常则返回 None。
    """
    try:
        # 获取当前日期并格式化
        current_date = datetime.now().date()
        formatted_date = current_date.strftime("%Y-%m-%d")
        return formatted_date
    except Exception as e:
        # 可选：记录异常信息（如写入日志）
        print(f"获取日期时发生错误：{e}")
        return ""  # 或者返回空字符串 ""，根据业务需求决定

def extract_and_write_excel_data(
    src_file_path,
    src_sheet_name,
    dest_file_path,
    dest_sheet_name,
    write_mode="append",
    condition_columns=[],
    column_mapping={}
):
    """
    从源Excel文件中提取符合条件的数据，并写入目标Excel文件的指定数据表中。

    参数:
        src_file_path (str): 源文件路径（支持相对路径和绝对路径）。
        src_sheet_name (str): 源数据表名称。
        dest_file_path (str): 目标文件路径（支持相对路径和绝对路径）。
        dest_sheet_name (str): 目标数据表名称。
        write_mode (str): 写入方式，"append"（默认）或 "overwrite"。
        condition_columns (list): 条件判定的表头列表。
        column_mapping (dict): 源列名到目标列名的映射。

    返回:
        dict: 包含操作状态和统计信息的字典。
    """
    try:
        # 路径规范化
        src_file_path = os.path.abspath(src_file_path)
        dest_file_path = os.path.abspath(dest_file_path)

        # ✅ 新增：使用 openpyxl 手动提取表头行
        wb = load_workbook(src_file_path)  # 加载工作簿
        if src_sheet_name not in wb.sheetnames:
            raise ValueError(f"源工作表 '{src_sheet_name}' 不存在。")
        ws = wb[src_sheet_name]

        # ✅ 新增：提取第一行（可能包含合并单元格）
        first_row_values = [cell.value for cell in ws[1]]
        first_row_values = [cell.value if cell.value is not None else "" for cell in ws[1]]

        # ✅ 新增：判断是否使用第二行作为表头
        if any(cell.value is None for cell in ws[1]):
            # 第一行有空值（合并单元格），使用第二行作为表头
            header_row = [cell.value for cell in ws[2]]
            skiprows = 2
        else:
            header_row = [cell.value for cell in ws[1]]
            skiprows = 1

        # ✅ 新增：使用 pandas 读取数据（不自动识别表头）
        src_df = pd.read_excel(
            src_file_path,
            sheet_name=src_sheet_name,
            header=None,  # 不自动识别表头
            skiprows=skiprows - 1,  # 跳过合并单元格行
        )

        # ✅ 新增：手动设置列名
        src_df.columns = header_row

        # ✅ 新增：调试输出列名
        print("源文件列名:", src_df.columns.tolist())

        total_rows = len(src_df)
        valid_rows = 0

        ############# 条件判断函数
        def is_valid_row(row):
            if not condition_columns:
                return True  # 无条件限制
            for col in condition_columns:
                if col not in row:
                    continue  # 忽略不存在的列
                
                cell_value = str(row[col]).strip()
                if cell_value != "无履职":
                    return False
            return True

        # 筛选合法数据
        filtered_df = src_df[src_df.apply(is_valid_row, axis=1)]
        valid_rows = len(filtered_df)

        # # 列映射处理
        # if column_mapping:
        #     target_columns = list(column_mapping.values())
        #     source_columns = list(column_mapping.keys())
        #     filtered_df = filtered_df[source_columns]
        #     filtered_df.columns = target_columns
        
        # 列映射处理
        if column_mapping:
            source_columns = list(column_mapping.keys())
            target_columns = list(column_mapping.values())

            # ✅ 新增：检查列名是否存在
            for col in source_columns:
                if col not in src_df.columns:
                    raise ValueError(f"源列 '{col}' 不存在于数据中，请检查列名拼写或数据结构。")

            filtered_df = filtered_df[source_columns]
            filtered_df.columns = target_columns

        # 写入目标文件
        with pd.ExcelWriter(dest_file_path, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            if write_mode == "overwrite":
                # 清空目标表
                if os.path.exists(dest_file_path):
                    wb = load_workbook(dest_file_path)
                    if dest_sheet_name in wb.sheetnames:
                        wb.remove(wb[dest_sheet_name])
                    wb.save(dest_file_path)
            filtered_df.to_excel(writer, sheet_name=dest_sheet_name, index=False)

        return {
            "success": True,
            "total_rows": total_rows,
            "valid_rows": valid_rows
        }

    except Exception as e:
        # 异常处理
        print(f"操作失败: {e}")
        return {
            "success": False,
            "total_rows": 0,
            "valid_rows": 0
        }

def process_excel_data(
    src_file_path: str,
    src_sheet_name: str,
    dest_file_path: str,
    dest_sheet_name: str,
    count_header: str,
    result_header: str,
    condition_header: str,
    serial_header: str = "",        # 序号列表头名称
    add_new_keys: bool = False,     # 是否添加新键
    add_new_rows: bool = False      # ✅ 新增参数：是否将未匹配的键追加到目标表中
    ):
    """
    从源 Excel 文件中读取数据，统计指定列的值，并将结果写入目标文件的指定工作表。

    参数:
        src_file_path       (str): 源文件路径（支持相对/绝对路径）。
        src_sheet_name      (str): 源数据表名称。
        dest_file_path      (str): 目标文件路径（支持相对/绝对路径）。
        dest_sheet_name     (str): 目标数据表名称。
        count_header        (str): 目标表中需要统计的列名（键）。
        result_header       (str): 目标表中存储统计结果的列名（值）。
        condition_header    (str): 源表中作为统计条件的列名。
        serial_header       (str): 序号列表头名称。
        add_new_keys        (bool): 指示是否添加新键（即统计结果中未出现的键）
        add_new_rows        (bool): 指示是否将未匹配的键追加到目标表中。
                                   - True: 未匹配的键将被追加为新行。
                                   - False: 未匹配的键将被忽略。

    返回:
        dict: 包含操作状态和统计信息的字典。
    """
    try:
        # 路径规范化
        src_file_path = os.path.abspath(src_file_path)
        dest_file_path = os.path.abspath(dest_file_path)

        # 检查源文件和目标文件是否存在
        if not os.path.exists(src_file_path):
            return {"success": False, "total_rows": 0, "statistics": {}, "error": "源文件不存在"}

        # 使用 openpyxl 手动读取源表头（处理合并单元格）
        src_wb = load_workbook(src_file_path)
        if src_sheet_name not in src_wb.sheetnames:
            return {"success": False, "total_rows": 0, "statistics": {}, "error": f"源工作表 '{src_sheet_name}' 不存在"}
        src_ws = src_wb[src_sheet_name]

        # 提取第一行（可能包含合并单元格）
        first_row_values = [cell.value for cell in src_ws[1]]
        first_row_values = [cell.value if cell.value is not None else "" for cell in src_ws[1]]

        # 判断是否使用第二行作为表头
        if any(cell.value is None for cell in src_ws[1]):
            header_row = [cell.value for cell in src_ws[2]]
            skiprows = 2
        else:
            header_row = first_row_values
            skiprows = 1

        # 使用 pandas 读取源数据
        src_df = pd.read_excel(
            src_file_path,
            sheet_name=src_sheet_name,
            header=None,
            # skiprows=skiprows - 1,
            skiprows=skiprows

        )
        src_df.columns = header_row

        # 检查源表中是否存在指定条件列
        if condition_header not in src_df.columns:
            return {
                "success": False,
                "total_rows": 0,
                "statistics": {},
                "error": f"源表中不存在列 '{condition_header}'"
            }

        # 初始化统计字典
        statistics = {}

        # 如果目标文件存在，读取目标表数据（用于初始化统计项）
        if os.path.exists(dest_file_path):
            dest_wb = load_workbook(dest_file_path)
            if dest_sheet_name in dest_wb.sheetnames:
                # ✅ 修改点：使用 dest_df_temp 而不是 dest_ws 来读取 count_header 列的值
                dest_df_temp = pd.read_excel(dest_file_path, sheet_name=dest_sheet_name)
                if count_header not in dest_df_temp.columns or result_header not in dest_df_temp.columns:
                    return {
                        "success": False,
                        "total_rows": 0,
                        "valid_rows": 0,
                        "statistics": {},
                        "error": f"目标表中不存在列 '{count_header}' 或 '{result_header}'"
                    }

                # ✅ 修改点：使用 pandas 读取 count_header 列的值，跳过表头
                count_values = dest_df_temp[count_header].dropna().tolist()
                statistics = {value: 0 for value in count_values}
        else:
            statistics = {}

        # 统计源数据
        total_rows = len(src_df)
        valid_rows = 0

        for _, row in src_df.iterrows():
            value = row[condition_header]

            if add_new_keys:
                # ✅ 如果允许添加新键，则直接增加计数，自动初始化为1
                statistics[value] = statistics.get(value, 0) + 1
                valid_rows += 1
            else:
                # ✅ 原有逻辑：仅当存在时才增加
                if value in statistics:
                    statistics[value] += 1
                    valid_rows += 1

        # 写入结果到目标文件
        with pd.ExcelWriter(dest_file_path, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            # 如果目标表不存在，则创建新表
            if not os.path.exists(dest_file_path) or dest_sheet_name not in load_workbook(dest_file_path).sheetnames:
                pd.DataFrame(columns=[count_header, result_header]).to_excel(
                    writer, sheet_name=dest_sheet_name, index=False
                )
                # 新建工作表后，初始化dest_df为空的DataFrame
                dest_df = pd.DataFrame(columns=[count_header, result_header])
            else:
                # ✅ 修改点：使用 writer 中的当前工作簿数据读取目标表（关键修改）
                dest_df = pd.read_excel(writer, sheet_name=dest_sheet_name)
                # 检查必要列的存在
                if count_header not in dest_df.columns or result_header not in dest_df.columns:
                    return {
                        "success": False,
                        "total_rows": 0,
                        "valid_rows": 0,
                        "statistics": {},
                        "error": f"目标表中不存在列 '{count_header}' 或 '{result_header}'"
                    }
                    
            # ✅ 修改点4：将列名转换为列字母
            if count_header in dest_df.columns and result_header in dest_df.columns:
                count_col_letter = get_column_letter(dest_df.columns.get_loc(count_header) + 1)
                result_col_letter = get_column_letter(dest_df.columns.get_loc(result_header) + 1)

                # 更新统计结果
                for index, row in dest_df.iterrows():
                    key = row[count_header]
                    if key in statistics:
                        dest_df.at[index, result_header] = statistics[key]
                        
                # ✅ 新增逻辑：将未匹配的键追加到目标表中
                if add_new_rows:
                    existing_keys = set(dest_df[count_header])
                    new_keys = [k for k in statistics.keys() if k not in existing_keys]
                    # 创建新行数据
                    new_rows = []
                    for key in new_keys:
                        new_rows.append({count_header: key, result_header: statistics[key]})
                    # 追加到目标 DataFrame
                    if new_rows:
                        dest_df = pd.concat([dest_df, pd.DataFrame(new_rows)], ignore_index=True)
                        
                # ✅ 新增：处理序号列逻辑
                if serial_header and serial_header.strip() != "":
                    # 检查序号列是否存在
                    if serial_header not in dest_df.columns:
                        # 不存在：在最左端插入新列
                        dest_df.insert(0, serial_header, range(1, len(dest_df) + 1))
                    else:
                        # 存在：填充从1开始的递增序号（忽略表头）
                        dest_df[serial_header] = range(1, len(dest_df) + 1)

                # 写回目标文件（✅ 确保使用当前 writer 的工作簿）
                dest_df.to_excel(writer, sheet_name=dest_sheet_name, index=False)


        return {
            "success": True,
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "statistics": statistics
        }

    except Exception as e:
        return {
            "success": False,
            "total_rows": 0,
            "valid_rows": 0,
            "statistics": {},
            "error": str(e)
        }
             
# def match_and_update_excel(
#     source_file, 
#     source_sheet, 
#     source_key_col, 
#     source_value_col,
#     target_file, 
#     target_sheet, 
#     target_key_col, 
#     target_value_col
# ):
#     """
#     从源Excel文件提取映射关系，匹配并更新目标Excel文件中的数据
    
#     参数：
#         source_file (str): 源Excel文件路径（支持相对/绝对路径）
#         source_sheet (str): 源Excel中的工作表名称
#         source_key_col (str): 源数据中用于匹配的列标题
#         source_value_col (str): 源数据中需要提取的列标题
#         target_file (str): 目标Excel文件路径（支持相对/绝对路径）
#         target_sheet (str): 目标Excel中的工作表名称
#         target_key_col (str): 目标数据中用于匹配的列标题
#         target_value_col (str): 目标数据中需要更新的列标题
        
#     返回：
#         dict: 包含执行结果的字典，格式为：
#             {
#                 'success': bool,      # 操作是否成功
#                 'total_processed': int, # 总处理行数
#                 'total_matched': int,   # 匹配成功并更新的行数
#                 'error': str           # 错误信息（仅在失败时存在）
#             }
#     """
#     try:
#         # 初始化结果统计
#         result = {'success': True, 'total_processed': 0, 'total_matched': 0}
        
#         # 读取源数据并构建映射字典
#         source_df = pd.read_excel(source_file, sheet_name=source_sheet)
#         if source_key_col not in source_df.columns or source_value_col not in source_df.columns:
#             raise ValueError(f"源数据列名 {source_key_col} 或 {source_value_col} 不存在")
        
#         source_dict = dict(zip(source_df[source_key_col], source_df[source_value_col]))
        
#         # 读取目标数据
#         try:
#             target_df = pd.read_excel(target_file, sheet_name=target_sheet)
#         except FileNotFoundError:
#             raise FileNotFoundError(f"目标文件 {target_file} 不存在")
            
#         if target_key_col not in target_df.columns or target_value_col not in target_df.columns:
#             raise ValueError(f"目标数据列名 {target_key_col} 或 {target_value_col} 不存在")
            
#         # 统计处理行数
#         result['total_processed'] = len(target_df)
        
#         # 执行匹配更新操作
#         matched_count = 0
#         for index, row in target_df.iterrows():
#             key_value = str(row[target_key_col]).strip()
#             if key_value in source_dict:
#                 target_df.at[index, target_value_col] = source_dict[key_value]
#                 matched_count += 1
                
#         result['total_matched'] = matched_count
        
#         # 写入更新后的目标文件
#         file_exists = os.path.exists(target_file)
#         with pd.ExcelWriter(
#             target_file,
#             engine='openpyxl',
#             mode='a' if file_exists else 'w',
#             if_sheet_exists='replace' if file_exists else None
#         ) as writer:
#             target_df.to_excel(writer, sheet_name=target_sheet, index=False)
            
#         return result
        
#     except Exception as e:
#         return {
#             'success': False,
#             'total_processed': 0,
#             'total_matched': 0,
#             'error': str(e)
#         }

def match_and_update_excel(
    source_file, source_sheet, source_key_col, source_value_col,
    target_file, target_sheet, target_key_col, target_value_col
):
    """
    从源Excel文件提取映射关系，匹配并更新目标Excel文件中的数据
    
    参数：
        source_file (str): 源Excel文件路径
        source_sheet (str): 源Excel中的工作表名称
        source_key_col (str): 源数据中用于匹配的列标题
        source_value_col (str): 源数据中需要提取的列标题
        target_file (str): 目标Excel文件路径
        target_sheet (str): 目标Excel中的工作表名称
        target_key_col (str): 目标数据中用于匹配的列标题
        target_value_col (str): 目标数据中需要更新的列标题
        
    返回：
        dict: 包含执行结果的字典
    """
    try:
        # 初始化结果统计
        result = {'success': True, 'total_processed': 0, 'total_matched': 0}
        
        # 读取源数据并构建映射字典
        source_df = pd.read_excel(source_file, sheet_name=source_sheet)
        if source_key_col not in source_df.columns or source_value_col not in source_df.columns:
            raise ValueError(f"源数据列名 {source_key_col} 或 {source_value_col} 不存在")

        source_dict = dict(zip(source_df[source_key_col], source_df[source_value_col]))
        
        # ✅ 显式指定读取目标文件时，第一行为表头（header=0）
        try:
            target_df = pd.read_excel(target_file, sheet_name=target_sheet, header=0)
        except FileNotFoundError:
            raise FileNotFoundError(f"目标文件 {target_file} 不存在")
            
        if target_key_col not in target_df.columns or target_value_col not in target_df.columns:
            raise ValueError(f"目标数据列名 {target_key_col} 或 {target_value_col} 不存在")
        
        # ✅ 打印列名和前几行数据，用于调试
        print(f"目标文件列名：{list(target_df.columns)}")  # 调试输出
        print("目标文件前几行数据：")
        print(target_df.head(5))
        
        # ✅ 统计处理行数（不包括表头）
        result['total_processed'] = len(target_df)
        
        # ✅ 处理数据（跳过表头行）
        matched_count = 0
        for index, row in target_df.iterrows():
            key_value = str(row[target_key_col]).strip()
            if key_value in source_dict:
                target_df.at[index, target_value_col] = source_dict[key_value]
                matched_count += 1
        result['total_matched'] = matched_count
        
        # ✅ 写入目标文件
        file_exists = os.path.exists(target_file)
        with pd.ExcelWriter(
            target_file,
            engine='openpyxl',
            mode='a' if file_exists else 'w',
            if_sheet_exists='replace' if file_exists else None
        ) as writer:
            # ✅ 写入表头，确保只写入一次
            target_df.to_excel(writer, sheet_name=target_sheet, index=False, header=True)
            
        return result
        
    except Exception as e:
        return {
            'success': False,
            'total_processed': 0,
            'total_matched': 0,
            'error': str(e)
        }

def Total_excel_data(file_path, sheet_name, columns_to_stat, total_column_header):
    result = {}
    try:
        # 加载工作簿和工作表
        wb = openpyxl.load_workbook(file_path)
        ws = wb[sheet_name]
        
        # 获取表头行
        header_cells = next(ws.iter_rows(min_row=1, max_row=1))
        headers = [cell.value for cell in header_cells]
        
        # 查找"合计"列的位置
        total_col_idx = None
        if total_column_header:
            if total_column_header in headers:
                total_col_idx = headers.index(total_column_header) + 1  # 转换为列号
            else:
                # 插入新列到最右侧
                ws.insert_cols(ws.max_column + 1)
                new_col_letter = get_column_letter(ws.max_column)
                ws[f"{new_col_letter}1"] = "合计"
                total_col_idx = ws.max_column
                
                # 设置标题样式
                ws[f"{new_col_letter}1"].font = Font(bold=True)
        
        # 找到最长列的长度
        max_row = 1  # 至少包含表头
        for col in range(1, ws.max_column + 1):
            col_len = 1  # 表头行
            for row in range(2, ws.max_row + 1):
                if ws.cell(row=row, column=col).value is not None:
                    col_len += 1
            max_row = max(max_row, col_len)
        
        # 处理"合计"列的内容位置
        if total_column_header:
            if total_col_idx in headers:  # 已存在该列
                # 找到该列的最后一个非空单元格
                last_row = 1
                for row in range(2, max_row + 1):
                    if ws.cell(row=row, column=total_col_idx).value is not None:
                        last_row = row
                # 在最后一行写入"合计"
                ws.cell(row=last_row + 1, column=total_col_idx, value="合计")
                # 设置样式
                ws.cell(row=last_row + 1, column=total_col_idx).alignment = Alignment(horizontal='center', vertical='center')
                ws.cell(row=last_row + 1, column=total_col_idx).font = Font(bold=True)
            else:  # 新建列的情况
                # 找到最长列的最后一个非空单元格
                last_row = max_row
                # 在最后一行写入"合计"
                ws.cell(row=last_row + 1, column=total_col_idx, value="合计")
                # 设置样式
                ws.cell(row=last_row + 1, column=total_col_idx).alignment = Alignment(horizontal='center', vertical='center')
                ws.cell(row=last_row + 1, column=total_col_idx).font = Font(bold=True)
        
        # 处理统计列
        for col_header in columns_to_stat:
            if col_header not in headers:
                result[col_header] = -1  # 表头不存在
                continue
            
            col_idx = headers.index(col_header) + 1
            is_numeric = True
            total = 0
            
            # 判断列类型
            for row in range(2, max_row + 1):
                cell_value = ws.cell(row=row, column=col_idx).value
                if cell_value is None:
                    continue
                # 清理特殊字符
                cleaned_value = re.sub(r'[\x00-\x1F\x7F]', '', str(cell_value)).strip()
                try:
                    num = float(cleaned_value)
                    total += num
                except ValueError:
                    is_numeric = False
                    break
            
            # 重新遍历统计
            if is_numeric:
                total = 0
                for row in range(2, max_row + 1):
                    cell_value = ws.cell(row=row, column=col_idx).value
                    if cell_value is not None:
                        cleaned_value = re.sub(r'[\x00-\x1F\x7F]', '', str(cell_value)).strip()
                        try:
                            num = float(cleaned_value)
                            total += num
                        except ValueError:
                            pass
            else:
                count = 0
                for row in range(2, max_row + 1):
                    if ws.cell(row=row, column=col_idx).value is not None:
                        count += 1
                total = count
            
            result[col_header] = total
            
            # 写入统计结果
            target_row = max_row + 1 if total_column_header else max_row
            ws.cell(row=target_row, column=col_idx, value=total)
        
        # 保存工作簿
        wb.save(file_path)
        
    except Exception as e:
        print(f"处理Excel时发生错误: {str(e)}")
    
    return result

def sort_excel_data(file_path, sheet_name, column_header, sort_type, sort_order, move_type):
    try:
        # 读取整个 Excel 文件中的所有工作表
        xls = pd.ExcelFile(file_path)
        sheets = {name: xls.parse(name) for name in xls.sheet_names}
        
        # 检查目标工作表是否存在
        if sheet_name not in sheets:
            return {'bool': False, 'count': 0, 'error': f"工作表 '{sheet_name}' 不存在"}

        # 获取目标工作表的 DataFrame
        df = sheets[sheet_name]
        headers = df.columns.tolist()
        data = df.values.tolist()

        # 检查目标列是否存在
        if column_header not in headers:
            return {'bool': False, 'count': 0, 'error': f"列 '{column_header}' 不存在"}

        # 获取目标列的索引
        col_index = df.columns.get_loc(column_header)

        # 定义排序键函数
        def key_func(row):
            val = row[col_index]
            if sort_type == 'number':
                return float(val) if val is not None else float('inf')
            elif sort_type == 'length':
                return len(str(val))
            elif sort_type == 'ASCII':
                return str(val)
            else:
                raise ValueError("不支持的排序类型")

        # 排序标志
        reverse = (sort_order == 'down')

        if move_type in ['all', 'serial']:
            # 对整行排序
            sorted_data = sorted(data, key=key_func, reverse=reverse)
            sorted_df = pd.DataFrame(sorted_data, columns=headers)

            if move_type == 'serial':
                # 重排最左侧的序号列
                sorted_df.iloc[:, 0] = range(1, len(sorted_df) + 1)

            sheets[sheet_name] = sorted_df

        elif move_type == 'only':
            # 仅对指定列排序，其他列保持原样
            col_data = [row[col_index] for row in data]
            if sort_type == 'number':
                col_data_sorted = sorted(col_data, key=lambda x: float(x) if x is not None else float('inf'), reverse=reverse)
            elif sort_type == 'length':
                col_data_sorted = sorted(col_data, key=lambda x: len(str(x)), reverse=reverse)
            elif sort_type == 'ASCII':
                col_data_sorted = sorted(col_data, key=lambda x: str(x), reverse=reverse)

            for i in range(len(data)):
                data[i][col_index] = col_data_sorted[i]

            sorted_df = pd.DataFrame(data, columns=headers)
            sheets[sheet_name] = sorted_df

        else:
            return {'bool': False, 'count': 0, 'error': "不支持的 move_type"}

        # 将所有工作表写回原文件
        with pd.ExcelWriter(file_path, mode='w') as writer:
            for s_name, s_df in sheets.items():
                s_df.to_excel(writer, sheet_name=s_name, index=False)

        return {'bool': True, 'count': len(data)}

    except Exception as e:
        return {'bool': False, 'count': 0, 'error': str(e)}

# 使用示例
if __name__ == "__main__":
    pass

    ############ 处理文件格式
    file_list = get_file_paths( ext="xls")
    for i in file_list:
        convert_xls_to_xlsx(i)
        
    ############ 处理复制文件模板
    now = get_formatted_date()
    new_f = now + "安质部周报统计.xlsx"
    print(copy_and_rename_file( src_path="./demo/统计模板.xlsx", dest_dir="./", new_name=new_f))
    
    ############ 统计处理数据
    
    judge_col = ["检查结果"]
    OP_DICT = {
        "工程所属项目部": "项目部",
        "工程名称": "工程名称",
        "督查日期": "监察日期",
        "问题描述": "监理履职不到位问题",
        "违章代码": "违章代码",
        "现场监理员": "责任人",
    }
    
    file_list = get_file_paths( ext="xlsx")
    for i in file_list:
        pass
    
        if is_keyword_in_filename( file_path=i, keyword="督查"):
            pass
        
            print( i + " >> Exist")
            
            print(
                extract_and_write_excel_data(
                    src_file_path=i,
                    src_sheet_name="督查导出",
                    dest_file_path=new_f,
                    dest_sheet_name="总表",
                    write_mode="append",
                    condition_columns=judge_col,
                    column_mapping=OP_DICT
                )
            )
            
            #################################
            print(
                process_excel_data(
                    src_file_path=new_f,
                    src_sheet_name="总表",
                    dest_file_path=new_f,
                    dest_sheet_name="项目部",
                    count_header="总监项目部",
                    result_header="监理未履职问题数",
                    condition_header="项目部",
                    serial_header=""
                )
            )
            
            print(
                Total_excel_data(
                    file_path=new_f,
                    sheet_name="项目部",
                    columns_to_stat=[ "总监项目部",	"监理未履职问题数"],
                    total_column_header="序号"
                )
            )
            
            #################################
            print(
                process_excel_data(
                    src_file_path=new_f,
                    src_sheet_name="总表",
                    dest_file_path=new_f,
                    dest_sheet_name="人员",
                    count_header="监理人员",
                    result_header="被查处监理履职问题数",
                    condition_header="责任人",
                    serial_header="序号",
                    add_new_keys=True,
                    add_new_rows=True,
                )
            )
            
            print(
                match_and_update_excel(
                    source_file=new_f,
                    source_sheet="总表",
                    source_key_col="责任人",
                    source_value_col="项目部",
                    target_file=new_f,
                    target_sheet="人员",
                    target_key_col="监理人员",
                    target_value_col="总监项目部",
                )
            )
            
            print(
                Total_excel_data(
                    file_path=new_f,
                    sheet_name="人员",
                    columns_to_stat=[ "监理人员", "总监项目部", "被查处监理履职问题数"],
                    total_column_header="序号"
                )
            )
            
        else:
            continue
        