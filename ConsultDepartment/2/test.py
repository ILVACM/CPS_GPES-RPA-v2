import json
from typing import Dict, Any, Union

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

import os
import json

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
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"json文件格式不正确: {json_path}")
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"处理过程中发生未知错误: {str(e)}")


import os
import pandas as pd
from openpyxl import load_workbook, Workbook

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
        def count_dict_levels(d):
            """
            计算嵌套字典的最大层级数
            """
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

            # 根据引导字典匹配并填写数据
            def match_and_fill(data_row, guide, depth=0):
                """
                递归匹配数据行和引导字典，并填写数据到目标单元格
                """
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
                            return match_and_fill(data_row, next_level, depth + 1)

                # 没有找到匹配项
                if len(data_row) > 0:
                    value_to_fill = data_row[-1] if data_row else ""
                    print(f"· {source_filename}:{source_sheet_name}_第{row_index}行-{{{value_to_fill}}} -> 匹配失败")
                else:
                    print(f"· {source_filename}:{source_sheet_name}_第{row_index}行- -> 匹配失败")
                stats["Failed"] += 1
                return False

            # 对当前行执行匹配和填写操作
            match_and_fill(row_data, guide_dict)

        # 保存目标工作簿
        target_wb.save(target_file_path)

        # 步骤4: 返回操作统计结果
        return stats

    except Exception as e:
        print(f"函数执行过程中发生错误: {str(e)}")
        return None

from win32com.client import Dispatch

def convert_xls_to_xlsx(xls_path, xlsx_path):
    excel = Dispatch("Excel.Application")
    workbook = excel.Workbooks.Open(xls_path)
    workbook.SaveAs(xlsx_path, FileFormat=51)  # 51 是 .xlsx 的格式代码
    workbook.Close()
    excel.Quit()

convert_xls_to_xlsx("input.xls", "output.xlsx")

# 测试代码示例
if __name__ == "__main__":
    # # 读取配置文件
    # with open("config.json", "r", encoding="utf-8") as f:
    #     config_data = json.load(f)

    plan = input("请输入需要填写的方案名称：\n")
    print("")

    config = Json_Check_Read( name=plan, json_path=r"config.json")
    if config:
        print("######### 当前校验结果为：TRUE ###########\n")
    else:
        print("\n！！！请检查配置文件或者输入后重启程序！！！\n")
        input("按任意按键退出程序········")
        exit()

    # # 调用函数格式化输出
    # formatted_output = Dict_format_display(config)
    # print(formatted_output)
    #
    # # 带颜色和Markdown格式的输出示例（虽然函数中未实际实现颜色和Markdown，但参数已支持）
    # formatted_output_with_options = Dict_format_display(
    #     config,
    #     indent_size=2,
    #     current_level=0,
    #     use_color=True,
    #     use_markdown=True
    # )

    print("\n" + "="*50 + "\n")

    # print("\n带选项的输出:")
    # print(formatted_output_with_options)

    result = xlsx_Fill_ExcelForm( source_file_path=r"./temp/ConditionSum.xlsx", source_sheet_name="Sheet1", guide_dict=config, target_file_path=r"./temp/第三方督查计划管控.xlsx", target_sheet_name="一周报")
    print(result)
