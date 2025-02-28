"""数据预处理脚本"""
import os
from collections import defaultdict
from typing import Literal

import pandas as pd

RAW_DATA_PATH = "raw_data/"
USE_DATA_PATH = "database_in_use/"
MID_DATA_PATH = "data/"


def merge_csv_files(source_path: str, out_path: str) -> None:
    """
    将源文件夹中的CSV文件根据前缀合并，并保存到目标文件夹中。
    Args:
        source_path (str): 要合并的CSV文件所在的文件夹路径。
        out_path (str): 合并后的CSV文件保存的文件夹路径。
    """
    # 根据文件前缀分组
    file_groups = defaultdict(list)
    for file_name in os.listdir(source_path):
        if file_name.endswith(".csv") and "字段释义" not in file_name:
            prefix = file_name.rsplit("_", 1)[0]
            file_groups[prefix].append(os.path.join(source_path, file_name))

    # 将相同前缀的文件合并
    for prefix, file_list in file_groups.items():
        merged_df = pd.concat(
            (pd.read_csv(file, index_col=0) for file in file_list), ignore_index=True
        )
        output_file = os.path.join(out_path, f"{prefix}.csv")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        merged_df.to_csv(output_file, index=False)


def compress_error_lines(df: pd.DataFrame) -> pd.DataFrame:
    """
    将记录中连续的error行压缩为首尾两行。

    Args:
        df (pandas.DataFrame): 要处理的DataFrame。

    Returns:
        pandas.DataFrame: 保留了非error记录和连续的error记录首尾两行的DataFrame。
    """
    # 判断每一行是否包含 "error"（不区分大小写）
    error_flag = df.apply(
        lambda row: row.astype(str).str.contains("error", case=False).any(), axis=1
    )

    # 记录要保留的行索引
    indices_to_keep = []
    n = len(df)
    index = 0
    while index < n:
        if not error_flag.iloc[index]:  # 非error行
            indices_to_keep.append(index)
            index += 1
        else:  # error行
            start = index
            while index < n and error_flag.iloc[index]:  # 继续向后查找连续的error行
                index += 1
            end = index - 1
            if start == end:  # 只有一行error
                indices_to_keep.append(start)
            else:  #  多行error，保留首尾两行
                indices_to_keep.append(start)
                indices_to_keep.append(end)
    return df.iloc[indices_to_keep].reset_index(drop=True)


def convert_to_numeric(value) -> float | Literal[-1]:
    """
    将值转换为浮点类型，无法转换的返回-1。

    Args:
        value (str): 要转换的值。

    Returns:
        float / -1: 成功转换后的数值，无法转换时返回-1。
    """
    try:
        return float(value)
    except ValueError:
        return -1


def is_steady_value(value: float, threshold: float = 69) -> bool:
    """
    判断电流值是否为稳定值。

    Args:
        value (float): 要判断的电流值。
        threshold (float): 稳定值的阈值，默认为58。

    Returns:
        bool: 如果值小于等于阈值，则返回True；否则返回False。
    """
    return value <= threshold


def process_ajia_data() -> None:
    """处理A架数据"""
    # 读取csv文件
    df_ajia = pd.read_csv(f"{MID_DATA_PATH}Ajia_plc_1.csv")

    # 压缩连续的error行
    df_ajia = compress_error_lines(df_ajia)

    # 将 Ajia-3_v 和 Ajia-5_v 列转换为浮点类型，无法转换的设为 -1
    df_ajia["Ajia-3_v"] = df_ajia["Ajia-3_v"].apply(convert_to_numeric)
    df_ajia["Ajia-5_v"] = df_ajia["Ajia-5_v"].apply(convert_to_numeric)

    # 初始化 action 列，默认值为 'False'
    df_ajia["action"] = "False"
    df_ajia["check_current_presence"] = "False"
    df_ajia["current_status"] = "False"
    df_ajia["current_avg"] = df_ajia[["Ajia-3_v", "Ajia-5_v"]].mean(axis=1)

    current_events = []  # 记录电流事件
    start_index = -1  # 电流事件的开始索引
    end_index = -1  # 电流事件的结束索引

    # 判断起始时刻电流状态
    current_3 = bool(df_ajia.at[0, "Ajia-3_v"] > 0)
    current_5 = bool(df_ajia.at[0, "Ajia-5_v"] > 0)
    if current_3 and current_5:
        current_total = True
        df_ajia.loc[0, "check_current_presence"] = "有电流"
        start_index = 0
    else:
        current_total = False
        df_ajia.loc[0, "check_current_presence"] = "无电流"

    # 遍历每一行，判断开关机和电流状态
    for index in range(1, df_ajia.shape[0]):
        # 开机条件
        # 上一时刻为error，当前时刻大于等于0
        if df_ajia.loc[index - 1, "Ajia-3_v"] == -1 and (
            df_ajia.loc[index, "Ajia-3_v"] == 0
            or df_ajia.loc[index, "Ajia-3_v"] == "0"
            or df_ajia.at[index, "Ajia-3_v"] > 0
        ):
            df_ajia.loc[index, "action"] = "A架开机"
        if df_ajia.loc[index - 1, "Ajia-5_v"] == -1 and (
            df_ajia.loc[index, "Ajia-5_v"] == 0
            or df_ajia.loc[index, "Ajia-5_v"] == "0"
            or df_ajia.at[index, "Ajia-5_v"] > 0
        ):
            df_ajia.loc[index, "action"] = "A架开机"

        # 关机条件
        # 上一时刻大于等于0，当前时刻为error
        if df_ajia.loc[index, "Ajia-3_v"] == -1 and (
            df_ajia.loc[index - 1, "Ajia-3_v"] == 0
            or df_ajia.loc[index - 1, "Ajia-3_v"] == "0"
            or df_ajia.at[index - 1, "Ajia-3_v"] > 0
        ):
            df_ajia.loc[index, "action"] = "A架关机"
        if df_ajia.loc[index, "Ajia-5_v"] == -1 and (
            df_ajia.loc[index - 1, "Ajia-5_v"] == 0
            or df_ajia.loc[index - 1, "Ajia-5_v"] == "0"
            or df_ajia.at[index - 1, "Ajia-5_v"] > 0
        ):
            df_ajia.loc[index, "action"] = "A架关机"

        # 检查电流是否存在
        # 当前时刻大于0，上一时刻为0或error
        if df_ajia.at[index, "Ajia-5_v"] > 0 and (
            df_ajia.loc[index - 1, "Ajia-5_v"] == 0
            or df_ajia.loc[index - 1, "Ajia-5_v"] == "0"
            or df_ajia.loc[index - 1, "Ajia-5_v"] == -1
        ):
            current_5 = True
        if df_ajia.at[index, "Ajia-3_v"] > 0 and (
            df_ajia.loc[index - 1, "Ajia-3_v"] == 0
            or df_ajia.loc[index - 1, "Ajia-3_v"] == "0"
            or df_ajia.loc[index - 1, "Ajia-3_v"] == -1
        ):
            current_3 = True
        # 当前时刻为0或error，上一时刻大于0
        if (
            df_ajia.loc[index, "Ajia-5_v"] == 0
            or df_ajia.loc[index, "Ajia-5_v"] == "0"
            or df_ajia.loc[index, "Ajia-5_v"] == -1
        ) and df_ajia.at[index - 1, "Ajia-5_v"] > 0:
            current_5 = False
        if (
            df_ajia.loc[index, "Ajia-3_v"] == 0
            or df_ajia.loc[index, "Ajia-3_v"] == "0"
            or df_ajia.loc[index, "Ajia-3_v"] == -1
        ) and df_ajia.at[index - 1, "Ajia-3_v"] > 0:
            current_3 = False
        # 根据两者状态判断电流是否存在
        if not current_total and (current_3 and current_5):
            current_total = True
            df_ajia.loc[index, "check_current_presence"] = "有电流"
            start_index = index
        if current_total and not (current_3 and current_5):
            current_total = False
            df_ajia.loc[index, "check_current_presence"] = "无电流"
            end_index = index
            if (
                start_index != -1 and end_index - start_index > 3
            ):  # 只记录大于3行的电流事件
                current_events.append((start_index, end_index))

    # 标记电流事件中的上升值、峰值、稳定值
    for current_event in current_events:
        start_index, end_index = current_event
        rise = False
        steady = False

        # 判断起始时刻电流状态
        start_value = df_ajia.at[start_index, "current_avg"]
        if not is_steady_value(start_value):  # 起始时刻为非稳定值
            df_ajia.loc[start_index, "current_status"] = "上升值"
            rise = True
            index_max = start_index  # 记录峰值的索引
            value_max = start_value
        else:  # 起始时刻为稳定值
            steady = True

        # 遍历电流事件中的每一行
        index = start_index + 1
        while index < end_index:
            value = df_ajia.at[index, "current_avg"]
            if steady:  # 之前状态为稳定值
                if not is_steady_value(value):  # 此时刻为非稳定值，改为上升状态
                    if index == end_index - 1:  # 事件结束，标记峰值
                        df_ajia.loc[index, "current_status"] = "峰值"
                    else:
                        steady = False
                        df_ajia.loc[index, "current_status"] = "上升值"
                        rise = True
                        index_max = index  # 记录峰值的索引
                        value_max = value
            elif rise:  # 之前状态为上升值
                if not is_steady_value(value):  # 此时刻为非稳定值，继续上升状态
                    if value > value_max:  # 更新峰值
                        value_max = value
                        index_max = index
                    if index == end_index - 1:  # 事件结束，标记峰值
                        df_ajia.loc[index_max, "current_status"] = "峰值"
                else:  # 此时刻为稳定值，改为稳定状态
                    df_ajia.loc[index_max, "current_status"] = "峰值"  # 标记峰值
                    steady = True
                    df_ajia.loc[index, "current_status"] = "稳定值"
                    rise = False
            index += 1

    # 保存处理后的数据
    df_ajia.to_csv(f"{USE_DATA_PATH}Ajia_plc_1.csv", index=False)


if __name__ == "__main__":
    # # 合并CSV文件
    # merge_csv_files(RAW_DATA_PATH, MID_DATA_PATH)
    # merge_csv_files(RAW_DATA_PATH, USE_DATA_PATH)

    # # 生成设备参数详情表.csv
    # os.makedirs(USE_DATA_PATH, exist_ok=True)
    # device_param_info = pd.read_excel(f"{RAW_DATA_PATH}设备参数详情.xlsx", dtype=str)
    # device_param_info = device_param_info.replace("\n", "", regex=True)  # 去除换行符
    # device_param_info.to_csv(f"{MID_DATA_PATH}设备参数详情表.csv", index=False)
    # device_param_info.to_csv(f"{USE_DATA_PATH}设备参数详情表.csv", index=False)

    process_ajia_data()
