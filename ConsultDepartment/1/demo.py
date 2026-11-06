import pandas as pd
import openpyxl as xl
from openpyxl import load_workbook
import os
import win32com.client as win32
import pythoncom
import datetime
import re
# from pptx.dml.color import RGBColor
# from pptx.util import Cm, Pt
# from pptx import Presentation

from typing import Union
from collections import defaultdict

import os
import shutil
from datetime import datetime

from pathlib import Path

#-----------------------------------------

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
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
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

def count_matching_rows( df, column_name, conditions):
    """
    统计指定列中符合多条件匹配的行数

    参数：
        df (DataFrame): 已加载的Excel数据表
        column_name (str): 目标列的表头名称
        conditions (list): 匹配条件列表（支持数值/字符串的多值匹配）

    返回：
        int: 匹配的行数，出错时返回-1
    """
    try:
        # 校验输入类型
        if not isinstance(column_name, str) or not isinstance(conditions, list):
            raise TypeError("参数类型错误")

        # 检查列是否存在
        if column_name not in df.columns:
            raise KeyError(f"列名 '{column_name}' 不存在")

        # 获取目标列数据
        target_col = df[column_name]

        # 构建多条件匹配掩码
        if target_col.dtype == 'object':  # 字符串类型列
            mask = target_col.isin(conditions)
        else:  # 数值类型列
            mask = target_col.between(min(conditions), max(conditions))

        return mask.sum()

    except KeyError as e:
        print(f"列名错误: {e}")
        return -1
    except TypeError as e:
        print(f"类型错误: {e}")
        return -1
    except Exception as e:
        print(f"未知错误: {e}")
        return -1

def count_fuzzy_matches( df, column_name, conditions):
    """
    统计指定列中符合多条件模糊匹配的行数

    参数：
        df (DataFrame): 已加载的Excel数据表
        column_name (str): 目标列的表头名称
        conditions (list): 匹配子字符串列表（支持多条件模糊匹配）

    返回：
        int: 匹配的行数，出错时返回-1
    """
    try:
        # 校验参数类型合法性
        if not isinstance(column_name, str) or not isinstance(conditions, list):
            raise TypeError("参数类型必须为(str, list)")

        # 检查列是否存在
        if column_name not in df.columns:
            raise KeyError(f"列名 '{column_name}' 不存在")

        # 处理空条件列表的特殊情况
        if len(conditions) == 0:
            return 0

        # 生成转义后的正则表达式模式
        escaped_conditions = [re.escape(str(c)) for c in conditions]
        pattern = '|'.join(escaped_conditions)

        # 执行模糊匹配
        mask = df[column_name].str.contains(
            pattern,
            case=False,  # 不区分大小写
            na=False,  # 将NaN视为False
            regex=True  # 启用正则表达式
        )

        return mask.sum()

    except KeyError as e:
        print(f"列名错误: {e}")
        return -1
    except TypeError as e:
        print(f"类型错误: {e}")
        return -1
    except re.error as e:
        print(f"正则表达式错误: {e}")
        return -1
    except Exception as e:
        print(f"未知错误: {e}")
        return -1

def sum_column( df, column_name):
    """
    统计DataFrame中指定数值列的总和，包含异常处理

    参数：
    df : DataFrame - pandas读取的Excel数据表
    column_name : str - 需要求和的列名

    返回值：
    float - 求和结果（出错时返回None）
    """
    try:
        # 将目标列强制转换为数值类型（非数值转为NaN）
        numeric_series = pd.to_numeric(df[column_name], errors='coerce')

        # 检查是否存在无效的非数值数据
        if numeric_series.isna().any():
            raise ValueError(f"列 '{column_name}' 包含无法转换为数值的数据")

        # 计算并返回总和
        return numeric_series.sum()

    except KeyError:
        print(f"错误：列名 '{column_name}' 不存在")
        return None
    except ValueError as ve:
        print(ve)
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None

def count_conditional_values( df, column_name, condition):
    """
    统计指定列满足条件的元素数量（支持>、<、>=、<=、==、!=运算符）

    参数：
    df : DataFrame - pandas读取的Excel数据表
    column_name : str - 目标列名
    condition : str - 条件表达式（如">50"、"<=100"、"==200"）

    返回值：
    int - 满足条件的元素数量（出错时返回None）
    """
    try:
        # 列存在性校验
        if column_name not in df.columns:
            raise KeyError(f"列名 '{column_name}' 不存在")

        # 转换为数值类型
        numeric_series = pd.to_numeric(df[column_name], errors='coerce')

        # 条件解析（支持6种运算符）
        pattern = r"^(>=|<=|>|<|==|!=)\s*(\d+\.?\d*)$"
        match = re.match(pattern, condition.strip())
        if not match:
            raise ValueError("条件格式错误，示例：'>50', '<=100', '==200'")

        operator, value = match.groups()
        value = float(value) if '.' in value else int(value)

        # 应用条件判断
        if operator == ">":
            mask = numeric_series > value
        elif operator == "<":
            mask = numeric_series < value
        elif operator == ">=":
            mask = numeric_series >= value
        elif operator == "<=":
            mask = numeric_series <= value
        elif operator == "==":
            mask = numeric_series == value
        elif operator == "!=":
            mask = numeric_series != value

        # 统计有效数据（排除NaN）
        count = mask.sum()

        # 检查是否全部为NaN
        if numeric_series.isna().all():
            raise ValueError(f"列 '{column_name}' 所有数据均为无效数值")

        return int(count)

    except KeyError as ke:
        print(f"错误：{ke}")
        return None
    except ValueError as ve:
        print(f"参数错误：{ve}")
        return None
    except TypeError as te:
        print(f"类型错误：列 '{column_name}' 包含非数值数据")
        return None
    except Exception as e:
        print(f"未知错误：{str(e)}")
        return None

def get_current_date():
    """
    获取当前系统日期并返回包含年月日的字典

    返回：
    dict - 包含Year/Month/Day键的字典（出错时返回None）
    """
    date_dict = {'Year': None, 'Month': None, 'Day': None}

    try:
        from datetime import datetime  # 延迟导入以便捕获导入错误

        # 获取当前系统时间
        now = datetime.now()

        # 提取日期组件
        date_dict['Year'] = now.year
        date_dict['Month'] = now.month
        date_dict['Day'] = now.day

        return date_dict

    except ImportError:
        print("错误：无法导入datetime模块")
        return None
    except AttributeError as ae:
        print(f"属性错误：{str(ae)}")
        return None
    except Exception as e:
        print(f"未知错误：{str(e)}")
        return None

def generate_report():
    """
    生成基建作业报告，所有数值通过变量管理
    返回格式化的报告字符串
    """
    # 基础配置数据
    config = {
        # 日期信息
        "date": {"year": 2023, "month": 10, "day": 19},

        # 项目数量配置
        "projects": {
            "main_network": 48,
            "distribution_network": 53,
            "small_infra": 0,
            "regions": {
                "电白": 14,
                "高州": 5,
                "化州": 5,
                "茂名茂港": 2,
                "茂南": 9,
                "信宜": 18,
                "项目中心": 48
            }
        },

        # 施工人员配置
        "personnel": {
            "total": 914,
            "large_operations": {
                "main_network": 1,  # 主网50人以上作业
                "distribution_network": 0  # 配网20人以上作业
            }
        },

        # 风险等级配置
        "risks": {
            "medium": 23,
            "high": {
                "total": 0,
                "regions": {
                    "电白": 0,
                    "高州": 0,
                    "化州": 0,
                    "茂名茂港": 0,
                    "茂南": 0,
                    "信宜": 0,
                    "项目中心": 0
                }
            }
        }
    }

    try:
        # 生成地区项目分布字符串
        region_items = "，".join(
            [f"{region}{count}"
             for region, count in config["projects"]["regions"].items()]
        )

        # 生成高风险地区分布字符串
        high_risk_regions = "，".join(
            [f"{region}{count}"
             for region, count in config["risks"]["high"]["regions"].items()]
        )

        # 构建报告模板
        report = f"""
茂名局{config['date']['year']}年{config['date']['month']}月{config['date']['day']}日基建施工作业计划数：
主网{config['projects']['main_network']}项，配网{config['projects']['distribution_network']}项，小型基建{config['projects']['small_infra']}项（{region_items}），共计{sum(config['projects']['regions'].values())}项
施工人数合计{config['personnel']['total']}人
中风险及以上作业{config['risks']['medium']}项（高风险{config['risks']['high']['total']}项[{high_risk_regions}]；中风险{config['risks']['medium']}项）
主网50人以上作业{config['personnel']['large_operations']['main_network']}项，配网20人以上作业{config['personnel']['large_operations']['distribution_network']}项；
        """.strip()

        return report

    except KeyError as e:
        print(f"配置键错误: 缺失关键配置项 {e}")
        return ""
    except TypeError as e:
        print(f"类型错误: 配置项类型不正确 {e}")
        return ""
    except Exception as e:
        print(f"生成报告时发生未知错误: {str(e)}")
        return ""

def write_to_file(content: str, file_path: str) -> bool:
    """
    将文本内容写入指定文件

    参数：
    content -- 要写入的字符串内容
    file_path -- 文件路径（支持绝对/相对路径）

    返回：
    bool -- 写入成功返回True，失败返回False

    异常处理：
    - 自动创建不存在的目录
    - 处理文件权限问题
    - 捕获无效路径等错误
    """
    try:
        # 规范化路径处理
        normalized_path = os.path.abspath(os.path.expanduser(file_path))
        target_dir = os.path.dirname(normalized_path)

        # 创建缺失目录（兼容Windows权限）
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            print(f"已创建目录：{target_dir}")

        # 写入文件（强制UTF-8编码）
        with open(normalized_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"文件已成功写入：{normalized_path}")
        return True

    except PermissionError:
        print(f"错误：没有写入权限 -> {normalized_path}")
    except FileNotFoundError:
        print(f"错误：无效路径 -> {normalized_path}")
    except OSError as e:
        print(f"系统错误：[{e.errno}] {e.strerror}")
    except Exception as e:
        print(f"未知错误：{type(e).__name__} - {str(e)}")

    return False

def replace_file_extension(file_path: str, new_extension: str) -> str:
    """
    智能替换文件路径扩展名（支持Windows路径格式）

    :param file_path: 原始文件路径（支持绝对/相对路径）
    :param new_extension: 新扩展名（可带或不带点）
    :return: 处理后的新路径字符串

    示例：
    replace_file_extension(r'C:\data\report.txt', 'csv')
    'C:\\data\\report.csv'
    replace_file_extension('image.tar.gz', 'xz')
    'image.tar.xz'
    """
    try:
        # 统一处理路径格式
        normalized_path = os.path.normpath(file_path)

        # 拆分路径和扩展名（自动处理多扩展名情况）
        base, _ = os.path.splitext(normalized_path)

        # 处理新扩展名格式
        if new_extension:
            # 自动补全扩展名点
            if not new_extension.startswith('.'):
                new_extension = '.' + new_extension
        else:
            # 允许清空扩展名
            new_extension = ''

        return base + new_extension
    except TypeError as e:
        raise ValueError("输入参数类型错误") from e
    except Exception as e:
        raise RuntimeError(f"路径处理失败: {str(e)}") from e

def count_power_supply_units(df: pd.DataFrame, column_name: str) -> dict:
    """
    解析指定列中格式化的层级字符串，统计供电局单位出现次数
    参数：
    df - pandas读取的DataFrame对象
    column_name - 需要解析的列名
    返回：
    统计结果字典及错误信息字典组成的元组
    """
    stats = defaultdict(int)
    errors = defaultdict(int)

    try:
        # 验证列是否存在
        if column_name not in df.columns:
            raise KeyError(f"列名'{column_name}'不存在")

        # 强制转换为字符串类型避免类型错误（参考网页17、18）
        series = df[column_name].astype(str)

        for idx, value in series.items():
            try:
                # 分割字符串并验证格式（参考网页16）
                parts = value.split('\\')
                if len(parts) < 4:
                    errors["层级不足"] += 1
                    continue

                # 提取第四个元素（索引3）
                target = parts[3].strip()
                if not target:
                    errors["空值元素"] += 1
                    continue

                # 分类统计逻辑
                if target.endswith("供电局"):
                    key = target[:-3]  # 移除末尾三个字符
                    # stats[key + "供电局"] += 1  # 保留完整名称
                    stats[key] += 1  # 保留完整名称
                else:
                    stats["项目管理中心"] += 1

            except Exception as e:
                errors[f"行{idx}解析错误"] += 1

    except KeyError as ke:
        errors["致命错误"] = str(ke)
    except Exception as e:
        errors["未知错误"] = str(e)

    return dict(stats), dict(errors)

def check_list(var):
    try:
        if isinstance(var, list):
            return len(var) > 0
        else:
            return False
    except Exception as e:
        return False

def extract_power_supply(file_path, sheet_name, header):
    """
    从指定Excel文件的指定工作表和列中，提取包含“供电局”的子字符串前的内容，并去重返回。
    
    参数:
        file_path (str): Excel文件路径（支持相对/绝对路径）
        sheet_name (str): 目标工作表名称
        header (str): 目标列名（表头）
    
    返回:
        list: 包含提取结果的字符串列表
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # 检查列是否存在
        if header not in df.columns:
            return []
        
        result = set()  # 使用集合去重
        column_data = df[header].dropna().astype(str)  # 转换为字符串并去除空值
        
        for cell in column_data:
            parts = cell.split('\\')  # 按反斜杠分割
            
            for part in parts:
                if "供电局" in part:
                    # 提取“供电局”前的部分
                    prefix = part.split("供电局", 1)[0]
                    result.add(prefix)
                    break  # 找到后立即处理下一行
        
        return list(result)  # 转换为列表返回
    
    except Exception as e:
        print(f"发生错误: {e}")
        return []

# 使用示例
if __name__ == "__main__":
    pass

    file_list = get_file_paths( ext="xls")
    for i in file_list:
        convert_xls_to_xlsx(i)

    file_list = get_file_paths( ext="xlsx")
    SheetName = "作业明细表"
    for i in file_list:
        # ====================================================
        data = pd.read_excel( i, sheet_name=SheetName)

        # 获取总行数和列数
        total_rows = data.shape[0]  # 总行数
        total_cols = data.shape[1]  # 总列数
        print(f"总行数：{total_rows}，总列数：{total_cols}")

        # ====================================================
        # target_header = "所属项目部"
        # temp = 0
        # match = ['设备监造总监项目部', '棠下柔直监理项目部']
        # if target_header in data.columns:
        #     col_index = data.columns.get_loc(target_header)  # 获取列索引
        #     temp = col_index
        #     print(temp)
        # else:
        #     raise ValueError(f"未找到表头 '{target_header}'")
        #
        # for i in range( total_rows - 1, -1, -1):  # 从最后一行倒序检查
        #     try:
        #         if data.iat[i, temp] in match:
        #             data = data.drop(index=data.index[i])
        #     except IndexError:
        #         continue

        # ====================================================
        
        Locate = []
        
        Locate = extract_power_supply( file_path=i, sheet_name=SheetName, header="单位")
        
        if check_list(Locate):
            Locate = Locate[0]
        else:
            Locate = ""
        
        # ====================================================
        PeiWang = count_fuzzy_matches( df=data, column_name="电压等级", conditions=[ '20kV及以下'])
        JiJian = count_fuzzy_matches( df=data, column_name="电压等级", conditions=[ '小型基建'])
        ZuWang = total_rows - PeiWang - JiJian

        Project, error = count_power_supply_units( df=data, column_name="单位")
        print(Project)
        print(error)

        # ====================================================

        Member_Number = sum_column( df=data, column_name="作业人数")

        # ====================================================

        FX = count_fuzzy_matches( df=data, column_name="风险等级", conditions=[ '中', '高'])
        Medium = count_fuzzy_matches( df=data, column_name="风险等级", conditions=[ '中'])
        High = count_fuzzy_matches( df=data, column_name="风险等级", conditions=[ '高'])

        # ====================================================

        temp_1 = data

        target_header = "风险等级"
        temp = 0
        match = ['高']
        if target_header in temp_1.columns:
            col_index = temp_1.columns.get_loc(target_header)  # 获取列索引
            temp = col_index
            print(temp)
        else:
            raise ValueError(f"未找到表头 '{target_header}'")

        for j in range(total_rows - 1, -1, -1):  # 从最后一行倒序检查
            try:
                if temp_1.iat[j, temp] not in match:
                    temp_1 = temp_1.drop(index=temp_1.index[j])
            except IndexError:
                continue

        FX_High, error = count_power_supply_units(df=temp_1, column_name="单位")
        print(FX_High)
        print(error)

        # ====================================================
        
        temp_1 = data

        target_header = "电压等级"
        temp = 0
        match = ['小型基建', '20kV及以下']
        if target_header in temp_1.columns:
            col_index = temp_1.columns.get_loc(target_header)  # 获取列索引
            temp = col_index
            print(temp)
        else:
            raise ValueError(f"未找到表头 '{target_header}'")

        for j in range(total_rows - 1, -1, -1):  # 从最后一行倒序检查
            try:
                if temp_1.iat[j, temp] in match:
                    temp_1 = temp_1.drop(index=temp_1.index[j])
            except IndexError:
                continue

        ZuWang50 = count_conditional_values( df=temp_1, column_name="作业人数", condition=">=50")

        # ====================================================

        temp_1 = data

        target_header = "电压等级"
        temp = 0
        match = [ '20kV及以下']
        if target_header in temp_1.columns:
            col_index = temp_1.columns.get_loc(target_header)  # 获取列索引
            temp = col_index
            print(temp)
        else:
            raise ValueError(f"未找到表头 '{target_header}'")

        for j in range(total_rows - 1, -1, -1):  # 从最后一行倒序检查
            try:
                if temp_1.iat[j, temp] not in match:
                    temp_1 = temp_1.drop(index=temp_1.index[j])
            except IndexError:
                continue

        PeiWang20 = count_conditional_values( df=temp_1, column_name="作业人数", condition=">=20")

        # ====================================================

        date = get_current_date()
        report = ""

        # 基础配置数据
        config = {
            # 日期信息
            "date": date,

            # 项目数量配置
            "projects": {
                "main_network": ZuWang,
                "distribution_network": PeiWang,
                "small_infra": JiJian,
                "regions": Project
            },

            # 施工人员配置
            "personnel": {
                "total": Member_Number,
                "large_operations": {
                    "main_network": ZuWang50,  # 主网50人以上作业
                    "distribution_network": PeiWang20  # 配网20人以上作业
                }
            },

            # 风险等级配置
            "risks": {
                "total": FX,
                "medium": Medium,
                "high": {
                    "total": High,
                    "regions": FX_High
                }
            }
        }

        try:
            # 生成地区项目分布字符串
            region_items = "，".join(
                [f"{region}{count}"
                 for region, count in config["projects"]["regions"].items()]
            )

            # 生成高风险地区分布字符串
            high_risk_regions = "，".join(
                [f"{region}{count}"
                 for region, count in config["risks"]["high"]["regions"].items()]
            )

            # 构建报告模板
            report = f"""
以下是对数据源文件"{i}"的统计结果：
{Locate}供电局{config['date']['Year']}年{config['date']['Month']}月{config['date']['Day']}日基建施工作业计划数：
主网{config['projects']['main_network']}项，配网{config['projects']['distribution_network']}项，小型基建{config['projects']['small_infra']}项（{region_items}），共计{total_rows}项
施工人数合计{config['personnel']['total']}人
中风险及以上作业{config['risks']['total']}项（高风险{config['risks']['high']['total']}项[{high_risk_regions}]；中风险{config['risks']['medium']}项）
主网50人以上作业{config['personnel']['large_operations']['main_network']}项，配网20人以上作业{config['personnel']['large_operations']['distribution_network']}项；
                """.strip()

            print(report)

        except KeyError as e:
            print(f"配置键错误: 缺失关键配置项 {e}")
        except TypeError as e:
            print(f"类型错误: 配置项类型不正确 {e}")
        except Exception as e:
            print(f"生成报告时发生未知错误: {str(e)}")

        target_path = replace_file_extension( file_path=i, new_extension="txt")
        print(write_to_file( content=report, file_path=target_path))

    input("\n>>>>>>>>>>>>>>>>>>>>>>>>请按任意键退出程序<<<<<<<<<<<<<<<<<<<<\n")