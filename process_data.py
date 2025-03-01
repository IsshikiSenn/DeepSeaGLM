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


def adjust_values(row):
    a5 = row["Ajia-5_v"]
    a3 = row["Ajia-3_v"]
    if a5 > 200 and a3 > 200:
        row["Ajia-5_v"] = 55
        row["Ajia-3_v"] = 55
    elif a5 > 200:
        row["Ajia-5_v"] = a3
    elif a3 > 200:
        row["Ajia-3_v"] = a5
    return row


def process_ajia_status(steady_threshold: int = 69, steady_window: int = 3) -> None:
    """
    判断A架开关机状态和电流状态

    Args:
        steady_threshold (int): 稳定值的阈值，小于等于这个值则认为是稳定值，默认值为69。
        steady_window (int): 稳定窗口大小，当连续稳定值数量大于等于这个值，则认为电流进入稳定状态，默认值为3。

    Returns:
        None
    """
    # 读取csv文件
    df_ajia = pd.read_csv(f"{MID_DATA_PATH}Ajia_plc_1.csv", index_col=False)

    # 将 Ajia-3_v 和 Ajia-5_v 列转换为浮点类型，无法转换的设为 -1
    df_ajia["Ajia-3_v"] = df_ajia["Ajia-3_v"].apply(lambda x: -1 if x == "error" else float(x))
    df_ajia["Ajia-5_v"] = df_ajia["Ajia-5_v"].apply(lambda x: -1 if x == "error" else float(x))
    df_ajia = df_ajia.apply(adjust_values, axis=1)

    # 初始化 action_ajia 列，默认值为 'False'
    df_ajia["action_ajia"] = "False"  # A架动作
    df_ajia["check_current_presence"] = "False"  # 有无电流
    df_ajia["current_status_ajia"] = "False"  # 电流状态
    df_ajia["current_avg"] = df_ajia[["Ajia-3_v", "Ajia-5_v"]].mean(axis=1)  # 电流均值

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
            df_ajia.loc[index, "action_ajia"] = "A架开机"
        if df_ajia.loc[index - 1, "Ajia-5_v"] == -1 and (
            df_ajia.loc[index, "Ajia-5_v"] == 0
            or df_ajia.loc[index, "Ajia-5_v"] == "0"
            or df_ajia.at[index, "Ajia-5_v"] > 0
        ):
            df_ajia.loc[index, "action_ajia"] = "A架开机"

        # 关机条件
        # 上一时刻大于等于0，当前时刻为error
        if df_ajia.loc[index, "Ajia-3_v"] == -1 and (
            df_ajia.loc[index - 1, "Ajia-3_v"] == 0
            or df_ajia.loc[index - 1, "Ajia-3_v"] == "0"
            or df_ajia.at[index - 1, "Ajia-3_v"] > 0
        ):
            df_ajia.loc[index, "action_ajia"] = "A架关机"
        if df_ajia.loc[index, "Ajia-5_v"] == -1 and (
            df_ajia.loc[index - 1, "Ajia-5_v"] == 0
            or df_ajia.loc[index - 1, "Ajia-5_v"] == "0"
            or df_ajia.at[index - 1, "Ajia-5_v"] > 0
        ):
            df_ajia.loc[index, "action_ajia"] = "A架关机"

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
    for start_index, end_index in current_events:
        rise = False
        steady = False
        steady_count = 0  # 连续稳定值计数
        last_not_steady_index = -1  # 记录最后一个非稳定值的索引

        # 判断起始时刻电流状态
        start_value = df_ajia.at[start_index, "current_avg"]
        if start_value > steady_threshold:  # 起始时刻为非稳定值
            df_ajia.loc[start_index, "current_status_ajia"] = "上升值"
            rise = True
            index_max = start_index  # 记录峰值的索引
            value_max = start_value
            last_not_steady_index = start_index
        else:  # 起始时刻为稳定值
            steady = True

        # 遍历电流事件中的每一行
        index = start_index + 1
        while index < end_index:
            value = df_ajia.at[index, "current_avg"]
            if steady:  # 之前状态为稳定值
                if value > steady_threshold:  # 此时刻为非稳定值，改为上升状态
                    if index == end_index - 1:  # 事件结束，标记峰值
                        df_ajia.loc[index, "current_status_ajia"] = "上升值 峰值"
                    else:
                        steady = False
                        df_ajia.loc[index, "current_status_ajia"] = "上升值"
                        rise = True
                        index_max = index  # 记录峰值的索引
                        value_max = value
                        last_not_steady_index = index
            elif rise:  # 之前状态为上升值
                if value > steady_threshold:  # 此时刻为非稳定值，继续上升状态
                    if value > value_max:  # 更新峰值
                        value_max = value
                        index_max = index
                    if index == end_index - 1:  # 事件结束，标记峰值
                        df_ajia.loc[index_max, "current_status_ajia"] = (
                            "峰值"
                            if df_ajia.loc[index_max, "current_status_ajia"] == "False"
                            else "上升值 峰值"
                        )
                    steady_count = 0
                    last_not_steady_index = index
                else:  # 此时刻为稳定值，记录连续稳定值
                    steady_count += 1
                    if steady_count >= steady_window or index == end_index - 1:  # 连续稳定值达到阈值，改为稳定状态
                        df_ajia.loc[index_max, "current_status_ajia"] = (
                            "峰值"
                            if df_ajia.loc[index_max, "current_status_ajia"] == "False"
                            else "上升值 峰值"
                        )  # 标记峰值
                        steady = True
                        df_ajia.loc[last_not_steady_index + 1, "current_status_ajia"] = "稳定值"
                        rise = False
                        steady_count = 0
            index += 1

    # 删除均值列
    df_ajia = df_ajia.drop(columns=["current_avg"])

    # 保存处理后的数据
    df_ajia.to_csv(f"{USE_DATA_PATH}Ajia_plc_1.csv", index=False)


def process_zhebidiaoche_status(steady_threshold: int = 7, steady_window: int = 3) -> None:
    """
    判断折臂吊车开关机状态

    Args:
        steady_threshold (int): 稳定值的阈值，小于等于这个值则认为是稳定值，默认值为7。
        steady_window (int): 稳定窗口大小，当连续稳定值数量大于等于这个值，则认为电流进入稳定状态，默认值为3。

    Returns:
        None
    """
    # 读取csv文件
    df_zhebidiaoche = pd.read_csv(
        f"{MID_DATA_PATH}device_13_11_meter_1311.csv", index_col=False
    )

    # 初始化 action_zhebidiaoche 列，默认值为 'False'
    df_zhebidiaoche["action_zhebidiaoche"] = "False"
    df_zhebidiaoche["current_status_zhebidiaoche"] = "False"

    # 判断开关机状态
    current_events = []  # 记录电流事件
    start_index = -1  # 电流事件的开始索引
    end_index = -1  # 电流事件的结束索引
    is_on = bool(df_zhebidiaoche.at[0, "13-11-6_v"] > 0)
    if is_on:
        start_index = 0
    for index in range(1, df_zhebidiaoche.shape[0]):
        if df_zhebidiaoche.at[index, "13-11-6_v"] > 0:
            if not is_on:
                df_zhebidiaoche.loc[index, "action_zhebidiaoche"] = "折臂吊车开机"
                is_on = True
                start_index = index
        else:
            if is_on:
                df_zhebidiaoche.loc[index, "action_zhebidiaoche"] = "折臂吊车关机"
                is_on = False
                end_index = index
                if start_index != -1:
                    current_events.append((start_index, end_index))
    if is_on:
        end_index = df_zhebidiaoche.shape[0] - 1
        current_events.append((start_index, end_index))

    # 标记电流事件中的最后高电流值
    for start_index, end_index in current_events:
        # 初始化
        steady_count = 0  # 连续稳定值计数
        is_steady = None  # 电流稳定状态
        last_not_steady_index = -1  # 记录最后一个非稳定值的索引

        # 判断起始时刻电流状态
        value = df_zhebidiaoche.at[start_index, "13-11-6_v"]
        if value > steady_threshold:
            is_steady = False
            last_not_steady_index = start_index
        else:
            is_steady = True

        # 遍历电流事件中的每一行
        index = start_index + 1
        while index < end_index:
            value = df_zhebidiaoche.at[index, "13-11-6_v"]
            if is_steady:  # 之前状态为稳定
                if (
                    value > steady_threshold
                ):  # 此时刻为非稳定值，改为不稳定状态，记录索引
                    is_steady = False
                    last_not_steady_index = index
            else:  # 之前状态为不稳定
                if (
                    value > steady_threshold
                ):  # 此时刻为不稳定值，继续不稳定状态，记录索引，重置连续稳定值计数
                    last_not_steady_index = index
                    steady_count = 0
                else:  # 此时刻为稳定值
                    steady_count += 1  # 增加连续稳定值
                    if (
                        steady_count >= steady_window
                    ):  # 连续稳定值达到阈值，改为稳定状态
                        df_zhebidiaoche.loc[
                            last_not_steady_index, "current_status_zhebidiaoche"
                        ] = "最后高电流值"
                        is_steady = True
                        steady_count = 0
            index += 1
        if not is_steady:
            df_zhebidiaoche.loc[
                last_not_steady_index, "current_status_zhebidiaoche"
            ] = "最后高电流值"

    # 保存处理后的数据
    df_zhebidiaoche.to_csv(f"{USE_DATA_PATH}device_13_11_meter_1311.csv", index=False)


def process_dp_status() -> None:
    """判断定位设备开关机状态"""
    # 读取csv文件
    df_dp = pd.read_csv(f"{MID_DATA_PATH}Port3_ksbg_9.csv", index_col=False)

    # 初始化 action_dp 列，默认值为 'False'
    df_dp["action_dp"] = "False"

    # 判断开关机状态
    is_on = bool(df_dp.at[0, "P3_33"] > 0)
    for index in range(1, df_dp.shape[0]):
        if df_dp.at[index, "P3_33"] > 0:
            if not is_on:
                df_dp.loc[index, "action_dp"] = "ON DP"
                is_on = True
        else:
            if is_on:
                df_dp.loc[index, "action_dp"] = "OFF DP"
                is_on = False

    # 保存处理后的数据
    df_dp.to_csv(f"{USE_DATA_PATH}Port3_ksbg_9.csv", index=False)


def process_actions():
    """判断A架、折臂吊车、定位设备的动作"""
    # 读取csv文件
    df_ajia = pd.read_csv(
        f"{USE_DATA_PATH}Ajia_plc_1.csv",
        index_col=False,
        usecols=[
            "Ajia-0_v",
            "Ajia-1_v",
            "Ajia-3_v",
            "Ajia-5_v",
            "csvTime",
            "action_ajia",
            "current_status_ajia",
        ],
        parse_dates=["csvTime"],
        date_format="%Y-%m-%d %H:%M:%S",
    )
    df_ajia["csvTime"] = df_ajia["csvTime"].dt.strftime("%Y-%m-%d %H:%M")
    df_ajia = df_ajia.set_index("csvTime")

    df_zhebidiaoche = pd.read_csv(
        f"{USE_DATA_PATH}device_13_11_meter_1311.csv",
        index_col=False,
        usecols=[
            "13-11-6_v",
            "csvTime",
            "action_zhebidiaoche",
            "current_status_zhebidiaoche",
        ],
        parse_dates=["csvTime"],
        date_format="%Y-%m-%d %H:%M:%S",
    )
    df_zhebidiaoche["csvTime"] = df_zhebidiaoche["csvTime"].dt.strftime(
        "%Y-%m-%d %H:%M"
    )
    df_zhebidiaoche = df_zhebidiaoche.set_index("csvTime")

    df_dp = pd.read_csv(
        f"{USE_DATA_PATH}Port3_ksbg_9.csv",
        index_col=False,
        usecols=["csvTime", "action_dp"],
        parse_dates=["csvTime"],
        date_format="%Y-%m-%d %H:%M:%S",
    )
    df_dp["csvTime"] = df_dp["csvTime"].dt.strftime("%Y-%m-%d %H:%M")
    df_dp = df_dp.set_index("csvTime")

    df_all = pd.merge(
        df_ajia,
        df_zhebidiaoche,
        how="outer",
        left_index=True,
        right_index=True,
    )
    df_all = pd.merge(
        df_all,
        df_dp,
        how="outer",
        left_index=True,
        right_index=True,
    )

    # 保存处理后的数据
    df_all.to_csv(f"{USE_DATA_PATH}actions.csv", index=True)


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

    process_ajia_status()

    # process_zhebidiaoche_status()

    # process_dp_status()

    process_actions()
