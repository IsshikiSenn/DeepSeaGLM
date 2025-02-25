import pandas as pd
from field_dict import field_dict


def calculate_uptime(start_time, end_time, shebeiname="折臂吊车"):
    """
    计算指定时间段内的开机时长，并返回三种格式的开机时长
    :param start_time: 查询的开始时间（字符串或 datetime 类型）
    :param end_time: 查询的结束时间（字符串或 datetime 类型）
    :param shebeiname: 设备名称，默认为 '折臂吊车'
    :return: 包含三种格式开机时长的字符串
    """
    print("-------calculate_uptime执行***计算开机时间-------")
    # 设备配置映射：设备名称 -> (文件路径, 开机状态, 关机状态)
    device_config = {
        "折臂吊车": (
            "database_in_use/device_13_11_meter_1311.csv",
            "折臂吊车开机",
            "折臂吊车关机",
        ),
        "A架": ("database_in_use/Ajia_plc_1.csv", "开机", "关机"),
        "DP": ("database_in_use/Port3_ksbg_9.csv", "ON_DP", "OFF_DP"),
    }

    # 检查设备名称是否有效
    if shebeiname not in device_config:
        raise ValueError(f"未知的设备名称: {shebeiname}")

    # 获取设备配置
    file_path, start_status, end_status = device_config[shebeiname]

    # 读取 CSV 文件
    df = pd.read_csv(file_path)

    # 将时间列转换为 datetime 类型
    df["csvTime"] = pd.to_datetime(df["csvTime"])

    # 将传入的开始时间和结束时间转换为 datetime 类型
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # 筛选出指定时间段内的数据
    df_filtered = df[(df["csvTime"] >= start_time) & (df["csvTime"] <= end_time)]

    # 初始化变量
    total_duration = pd.Timedelta(0)
    start_uptime = None

    # 遍历筛选后的数据
    for index, row in df_filtered.iterrows():
        if row["status"] == start_status:
            start_uptime = row["csvTime"]
        elif row["status"] == end_status and start_uptime is not None:
            end_uptime = row["csvTime"]
            total_duration += end_uptime - start_uptime
            start_uptime = None

    # 计算三种格式的开机时长
    seconds = total_duration.total_seconds()
    minutes = int(seconds / 60)
    hours = int(seconds // 3600)
    remaining_minutes = int((seconds % 3600) // 60)

    # 将小时和分钟格式化为两位数
    hours_str = f"{hours:02d}"  # 使用格式化字符串确保两位数
    minutes_str = f"{remaining_minutes:02d}"  # 使用格式化字符串确保两位数

    # 返回三种格式的开机时长
    result = {
        "function": "calculate_uptime",  # 说明这个返回结果来自哪个函数
        "result": (
            f"开机时长：{seconds}秒",
            f"开机时长：{minutes}分钟",
            f"开机时长：{hours_str}小时{minutes_str}分钟",
        ),
    }
    return result


def compute_operational_duration(start_time, end_time, device_name="A架"):
    """
    计算设备在指定时间段内的实际运行时长（有电流且不为0）。
    Params:
        start_time (str or pd.Timestamp): 开始时间，字符串格式或 pandas 的 Timestamp 对象。
        end_time (str or pd.Timestamp): 结束时间，字符串格式或 pandas 的 Timestamp 对象。
        device_name (str, optional): 设备名称，默认为 "A架"。
    Returns:
        tuple: 包含三种格式的实际运行时长的元组。
    Raises:
        ValueError: 当设备名称无效时抛出异常。
    """

    # 设备配置映射：设备名称 -> (文件路径, 开机状态, 关机状态)
    print("-------compute_operational_duration执行-------")
    device_config = {
        "A架": ("database_in_use/Ajia_plc_1.csv", "有电流", "无电流"),
    }
    # 检查设备名称是否有效
    if device_name not in device_config:
        raise ValueError(f"未知的设备名称: {device_name}")

    # 获取设备配置
    file_path, start_status, end_status = device_config[device_name]

    # 读取 CSV 文件
    df = pd.read_csv(file_path)

    # 将时间列转换为 datetime 类型
    df["csvTime"] = pd.to_datetime(df["csvTime"])

    # 将传入的开始时间和结束时间转换为 datetime 类型
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # 筛选出指定时间段内的数据
    df_filtered = df[(df["csvTime"] >= start_time) & (df["csvTime"] <= end_time)]

    # 初始化变量
    total_duration = pd.Timedelta(0)
    start_uptime = None
    # 遍历筛选后的数据
    for index, row in df_filtered.iterrows():
        if row["check_current_presence"] == start_status:
            start_uptime = row["csvTime"]
        elif row["check_current_presence"] == end_status and start_uptime is not None:
            end_uptime = row["csvTime"]
            total_duration += end_uptime - start_uptime
            start_uptime = None

    # 计算三种格式的开机时长
    seconds = total_duration.total_seconds()
    minutes = int(seconds / 60)
    hours = int(seconds // 3600)
    remaining_minutes = int((seconds % 3600) // 60)

    # 将小时和分钟格式化为两位数
    hours_str = f"{hours:02d}"  # 使用格式化字符串确保两位数
    minutes_str = f"{remaining_minutes:02d}"  # 使用格式化字符串确保两位数

    return (
        f"运行时长：{seconds}秒",
        f"运行时长：{minutes}分钟",
        f"运行时长：{hours_str}小时{minutes_str}分钟",
    )


def get_table_data(table_name, start_time, end_time, columns=None, status=None):
    """
    根据数据表名、开始时间、结束时间、列名和状态获取指定时间范围内的相关数据。

    参数:
    table_name (str): 数据表名
    start_time (str): 开始时间，格式为 'YYYY-MM-DD HH:MM:SS'
    end_time (str): 结束时间，格式为 'YYYY-MM-DD HH:MM:SS'
    columns (list): 需要查询的列名列表，如果为None，则返回所有列
    status (str): 需要筛选的状态（例如 "开机"、"关机"），如果为None，则不筛选状态

    返回:
    dict: 包含指定列名和对应值的字典，或错误信息
    """
    # 创建一个字典来存储元数据
    metadata = {
        "table_name": table_name,
        "start_time": start_time,
        "end_time": end_time,
        "columns": columns,
        "status": status,
    }

    try:
        df = pd.read_csv(f"database_in_use/{table_name}.csv")
    except FileNotFoundError:
        return {"error": f"数据表 {table_name} 不存在", "metadata": metadata}

    # 将csvTime列从时间戳转换为datetime类型
    df["csvTime"] = pd.to_datetime(df["csvTime"], unit="ns")  # 假设时间戳是纳秒级别

    # 将开始时间和结束时间转换为datetime类型
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)
    # 如果开始时间和结束时间是同一分钟
    if (
        start_time.minute == end_time.minute
        and start_time.hour == end_time.hour
        and start_time.day == end_time.day
    ):
        # 将开始时间设置为这一分钟的00秒
        start_time = start_time.replace(second=0)
        # 将结束时间设置为这一分钟的59秒
        end_time = end_time.replace(second=59)
    # 筛选指定时间范围内的数据
    filtered_data = df[(df["csvTime"] >= start_time) & (df["csvTime"] <= end_time)]

    if filtered_data.empty:
        return {
            "error": f"在数据表 {table_name} 中未找到时间范围 {start_time} 到 {end_time} 的数据",
            "metadata": metadata,
        }

    # 如果传入了 status 参数，则进一步筛选状态
    if status is not None:
        filtered_data = filtered_data[filtered_data["status"] == status]
        if filtered_data.empty:
            return {
                "error": f"在数据表 {table_name} 中未找到状态为 {status} 的数据",
                "metadata": metadata,
            }

    # 如果未指定列名，则返回所有列
    if columns is None:
        columns = filtered_data.columns.tolist()

    # 检查列名是否存在
    missing_columns = [
        column for column in columns if column not in filtered_data.columns
    ]
    if missing_columns:
        return {
            "error": f"列名 {missing_columns} 在数据表 {table_name} 中不存在",
            "metadata": metadata,
        }

    # 获取指定列名和对应的值
    result = {}
    for column in columns:
        if column == "csvTime":
            # 将时间格式化为字符串
            result[column] = (
                filtered_data[column].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
            )
        else:
            result[column] = filtered_data[column].values.tolist()

    # 返回结果和元数据
    return {"result": result, "metadata": metadata}


# 能耗计算
def load_and_filter_data(file_path, start_time, end_time, power_column):
    """
    加载 CSV 文件并筛选指定时间范围内的数据
    :param file_path: CSV 文件路径
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param power_column: 功率列名
    :return: 筛选后的 DataFrame
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {file_path} 未找到")

    # 确保时间列是 datetime 类型
    try:
        df["csvTime"] = pd.to_datetime(df["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    # 筛选特定时间范围内的数据
    filtered_data = df[
        (df["csvTime"] >= start_time) & (df["csvTime"] < end_time)
    ].copy()

    if filtered_data.empty:
        return None

    # 计算时间差（秒）
    filtered_data.loc[:, "diff_seconds"] = (
        filtered_data["csvTime"].diff().dt.total_seconds().shift(-1)
    )

    # 计算每个时间间隔的能耗（kWh）
    filtered_data.loc[:, "energy_kWh"] = (
        filtered_data["diff_seconds"] * filtered_data[power_column] / 3600
    )

    return filtered_data


def calculate_total_energy(start_time, end_time, device_name="折臂吊车"):
    """
    计算指定时间段内的总能耗
    :param start_time: 查询的开始时间（字符串或 datetime 类型）
    :param end_time: 查询的结束时间（字符串或 datetime 类型）
    :param device_name: 设备名称，默认为 '折臂吊车'
    :return: 总能耗（kWh，float 类型）
    """
    # 设备配置映射：设备名称 -> (表名, 功率列名)
    device_config = {
        "折臂吊车": ("device_13_11_meter_1311", "13-11-6_v"),
        "一号门架": ("device_1_5_meter_105", "1-5-6_v"),  # 一号门架的配置
        "二号门架": ("device_13_14_meter_1314", "13-14-6_v"),  # 二号门架的配置
        "绞车": ("device_1_15_meter_115", "1-15-6_v"),  # 添加绞车的配置
    }

    # 检查设备名称是否有效
    if device_name not in device_config:
        raise ValueError(f"未知的设备名称: {device_name}")

    # 获取设备配置
    table_name, power_column = device_config[device_name]

    # 读取 CSV 文件并计算能耗
    file_path = f"database_in_use/{table_name}.csv"
    try:
        filtered_data = load_and_filter_data(
            file_path, start_time, end_time, power_column
        )
        if filtered_data is None:
            return None
        total_energy = filtered_data["energy_kWh"].sum()
        return round(total_energy, 2)
    except Exception as e:
        raise ValueError(f"计算能耗时出错: {e}")


def calculate_total_deck_machinery_energy(start_time, end_time):
    """
    计算指定时间范围内甲板机械的能耗，包括折臂吊车、一号门架、二号门架、绞车，以及总能耗。
    Params:
        start_time (str): 指定时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'。
        end_time (str): 指定时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。
    Returns:
        dict: 包含甲板机械四个部分（折臂吊车、一号门架、二号门架、绞车）的能耗和总能耗（kWh）的字典，如果数据为空则返回 None。
    Raises:
        FileNotFoundError: 如果文件未找到。
        ValueError: 如果时间列转换失败。
    """
    file_path_zhebidiaoche = "database_in_use/device_13_11_meter_1311.csv"
    power_column_zhebidiaoche = "13-11-6_v"  # 折臂吊车液压-Pt有功功率,单位:kW

    file_path_mengjia1 = "database_in_use/device_1_5_meter_105.csv"
    power_column_mengjia1 = "1-5-6_v"  # 一号门架主液压泵-Pt有功功率,单位:kW

    file_path_mengjia2 = "database_in_use/device_13_14_meter_1314.csv"
    power_column_mengjia2 = "13-14-6_v"  # 二号门架主液压泵-Pt有功功率,单位:kW

    file_path_jiaoche = "database_in_use/device_1_15_meter_115.csv"
    power_column_jiaoche = "1-15-6_v"  # 绞车变频器-Pt有功功率,单位:kW

    try:
        df_zhebidiaoche = pd.read_csv(file_path_zhebidiaoche)
        df_mengjia1 = pd.read_csv(file_path_mengjia1)
        df_mengjia2 = pd.read_csv(file_path_mengjia2)
        df_jiaoche = pd.read_csv(file_path_jiaoche)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"文件未找到: {e}")

    try:
        df_zhebidiaoche["csvTime"] = pd.to_datetime(df_zhebidiaoche["csvTime"])
        df_mengjia1["csvTime"] = pd.to_datetime(df_mengjia1["csvTime"])
        df_mengjia2["csvTime"] = pd.to_datetime(df_mengjia2["csvTime"])
        df_jiaoche["csvTime"] = pd.to_datetime(df_jiaoche["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    filtered_data_zhebidiaoche = df_zhebidiaoche[
        (df_zhebidiaoche["csvTime"] >= start_time)
        & (df_zhebidiaoche["csvTime"] < end_time)
    ].copy()
    filtered_data_mengjia1 = df_mengjia1[
        (df_mengjia1["csvTime"] >= start_time) & (df_mengjia1["csvTime"] < end_time)
    ].copy()
    filtered_data_mengjia2 = df_mengjia2[
        (df_mengjia2["csvTime"] >= start_time) & (df_mengjia2["csvTime"] < end_time)
    ].copy()
    filtered_data_jiaoche = df_jiaoche[
        (df_jiaoche["csvTime"] >= start_time) & (df_jiaoche["csvTime"] < end_time)
    ].copy()

    if (
        filtered_data_zhebidiaoche.empty
        or filtered_data_mengjia1.empty
        or filtered_data_mengjia2.empty
        or filtered_data_jiaoche.empty
    ):
        return None

    filtered_data_zhebidiaoche.loc[:, "diff_seconds"] = (
        filtered_data_zhebidiaoche["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_mengjia1.loc[:, "diff_seconds"] = (
        filtered_data_mengjia1["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_mengjia2.loc[:, "diff_seconds"] = (
        filtered_data_mengjia2["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_jiaoche.loc[:, "diff_seconds"] = (
        filtered_data_jiaoche["csvTime"].diff().dt.total_seconds().shift(-1)
    )

    filtered_data_zhebidiaoche.loc[:, "energy_kWh"] = (
        filtered_data_zhebidiaoche["diff_seconds"]
        * filtered_data_zhebidiaoche[power_column_zhebidiaoche]
        / 3600
    )
    filtered_data_mengjia1.loc[:, "energy_kWh"] = (
        filtered_data_mengjia1["diff_seconds"]
        * filtered_data_mengjia1[power_column_mengjia1]
        / 3600
    )
    filtered_data_mengjia2.loc[:, "energy_kWh"] = (
        filtered_data_mengjia2["diff_seconds"]
        * filtered_data_mengjia2[power_column_mengjia2]
        / 3600
    )
    filtered_data_jiaoche.loc[:, "energy_kWh"] = (
        filtered_data_jiaoche["diff_seconds"]
        * filtered_data_jiaoche[power_column_jiaoche]
        / 3600
    )

    total_energy_zhebidiaoche = filtered_data_zhebidiaoche["energy_kWh"].sum()
    total_energy_mengjia1 = filtered_data_mengjia1["energy_kWh"].sum()
    total_energy_mengjia2 = filtered_data_mengjia2["energy_kWh"].sum()
    total_energy_jiaoche = filtered_data_jiaoche["energy_kWh"].sum()

    return {
        "折臂吊车":total_energy_zhebidiaoche,
        "一号门架":total_energy_mengjia1,
        "二号门架":total_energy_mengjia2,
        "绞车":total_energy_jiaoche,
        "总能耗":round(
            total_energy_zhebidiaoche
            + total_energy_mengjia1
            + total_energy_mengjia2
            + total_energy_jiaoche,
            2,
        ),
    }


def calculate_energy_consumption(start_time, end_time):
    """
    计算指定时间范围内的侧推的总能耗
    :param start_time: 开始时间（字符串或 datetime 类型）
    :param end_time: 结束时间（字符串或 datetime 类型）
    :return: 总能耗（kWh，float 类型），如果数据为空则返回 None
    """
    # 文件路径和功率列名直接定义在函数内部
    file_path = "database_in_use/Port3_ksbg_9.csv"
    power_column = "P3_18"  # 使用 "艏推功率反馈,单位:kW" 列

    try:
        # 加载 CSV 文件
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {file_path} 未找到")

    # 确保时间列是 datetime 类型
    try:
        df["csvTime"] = pd.to_datetime(df["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    # 筛选特定时间范围内的数据
    filtered_data = df[
        (df["csvTime"] >= start_time) & (df["csvTime"] < end_time)
    ].copy()

    if filtered_data.empty:
        return None

    # 计算时间差（秒）
    filtered_data.loc[:, "diff_seconds"] = (
        filtered_data["csvTime"].diff().dt.total_seconds().shift(-1)
    )

    # 计算每个时间间隔的能耗（kWh）
    filtered_data.loc[:, "energy_kWh"] = (
        filtered_data["diff_seconds"] * filtered_data[power_column] / 3600
    )

    # 计算总能耗
    total_energy = filtered_data["energy_kWh"].sum()

    return round(total_energy, 2)


def query_device_parameter(parameter_name_cn):
    """
    通过参数中文名查询设备参数信息
    :param parameter_name_cn: 参数中文名
    :param device_parameter_file: 设备参数详情表的文件路径，默认为'设备参数详情表.csv'
    :return: 返回包含参数信息的字典
    """
    print("-------query_device_parameter执行-------")
    # 读取设备参数详情表
    df = pd.read_csv("database_in_use/设备参数详情表.csv")

    # 检查参数中文名是否包含在 Channel_Text_CN 列中
    if not df["Channel_Text_CN"].str.contains(parameter_name_cn).any():
        raise ValueError(f"未找到包含 '{parameter_name_cn}' 的参数中文名")

    # 获取包含参数中文名的所有行
    parameter_info = df[df["Channel_Text_CN"].str.contains(parameter_name_cn)].iloc[0]

    # 将参数信息转换为字典
    parameter_dict = {
        "参数名": parameter_info["Channel_Text"],
        "参数中文名": parameter_info["Channel_Text_CN"],
        "参数下限": parameter_info["Alarm_Information_Range_Low"],
        "参数上限": parameter_info["Alarm_Information_Range_High"],
        "报警值的单位": parameter_info["Alarm_Information_Unit"],
        "报警值": parameter_info["Parameter_Information_Alarm"],
        "屏蔽值": parameter_info["Parameter_Information_Inhibit"],
        "延迟值": parameter_info["Parameter_Information_Delayed"],
        "安全保护设定值": parameter_info["Safety_Protection_Set_Value"],
        "附注": parameter_info["Remarks"],
    }
    return parameter_dict


def calculate_total_energy_consumption(start_time, end_time):
    """
    计算指定时间范围内推进系统的能耗，包括一号推进变频器、二号推进变频器、艏推、可伸缩推和总能耗。
    Params:
        start_time (str): 指定时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'。
        end_time (str): 指定时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。
    Returns:
        dict: 包含推进系统四个部分（一号推进变频器、二号推进变频器、艏推、可伸缩推）的能耗和总能耗（kWh）的字典，如果数据为空则返回 None。
    Raises:
        FileNotFoundError: 如果文件未找到。
        ValueError: 如果时间列转换失败。
    """
    # 文件路径和功率列名
    file_path_1 = "database_in_use/Port3_ksbg_8.csv"
    power_column_1 = "P3_15"  # 一号推进变频器功率反馈,单位:kW

    file_path_2 = "database_in_use/Port4_ksbg_7.csv"
    power_column_2 = "P4_16"  # 二号推进变频器功率反馈,单位:kW

    file_path_shoutui = "database_in_use/Port3_ksbg_9.csv"
    power_column_shoutui = "P3_18"  # 艏推功率反馈,单位:kW

    file_path_shensuotui = "database_in_use/Port4_ksbg_8.csv"
    power_column_shensuotui = "P4_21"  # 可伸缩推功率反馈,单位:kW

    try:
        # 加载 CSV 文件
        df1 = pd.read_csv(file_path_1)
        df2 = pd.read_csv(file_path_2)
        df_shoutui = pd.read_csv(file_path_shoutui)
        df_shensuotui = pd.read_csv(file_path_shensuotui)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"文件未找到: {e}")

    # 确保时间列是 datetime 类型
    try:
        df1["csvTime"] = pd.to_datetime(df1["csvTime"])
        df2["csvTime"] = pd.to_datetime(df2["csvTime"])
        df_shoutui["csvTime"] = pd.to_datetime(df_shoutui["csvTime"])
        df_shensuotui["csvTime"] = pd.to_datetime(df_shensuotui["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    # 筛选特定时间范围内的数据
    filtered_data_1 = df1[
        (df1["csvTime"] >= start_time) & (df1["csvTime"] < end_time)
    ].copy()
    filtered_data_2 = df2[
        (df2["csvTime"] >= start_time) & (df2["csvTime"] < end_time)
    ].copy()
    filtered_data_shoutui = df_shoutui[
        (df_shoutui["csvTime"] >= start_time) & (df_shoutui["csvTime"] < end_time)
    ].copy()
    filtered_data_shensuotui = df_shensuotui[
        (df_shensuotui["csvTime"] >= start_time) & (df_shensuotui["csvTime"] < end_time)
    ].copy()

    if (
        filtered_data_1.empty
        or filtered_data_2.empty
        or filtered_data_shoutui.empty
        or filtered_data_shensuotui.empty
    ):
        return None

    # 计算时间差（秒）
    filtered_data_1.loc[:, "diff_seconds"] = (
        filtered_data_1["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_2.loc[:, "diff_seconds"] = (
        filtered_data_2["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_shoutui.loc[:, "diff_seconds"] = (
        filtered_data_shoutui["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_shensuotui.loc[:, "diff_seconds"] = (
        filtered_data_shensuotui["csvTime"].diff().dt.total_seconds().shift(-1)
    )

    # 计算每个时间间隔的能耗（kWh）
    filtered_data_1.loc[:, "energy_kWh"] = (
        filtered_data_1["diff_seconds"] * filtered_data_1[power_column_1] / 3600
    )
    filtered_data_2.loc[:, "energy_kWh"] = (
        filtered_data_2["diff_seconds"] * filtered_data_2[power_column_2] / 3600
    )
    filtered_data_shoutui.loc[:, "energy_kWh"] = (
        filtered_data_shoutui["diff_seconds"]
        * filtered_data_shoutui[power_column_shoutui]
        / 3600
    )
    filtered_data_shensuotui.loc[:, "energy_kWh"] = (
        filtered_data_shensuotui["diff_seconds"]
        * filtered_data_shensuotui[power_column_shensuotui]
        / 3600
    )

    # 计算总能耗
    total_energy_1 = filtered_data_1["energy_kWh"].sum()
    total_energy_2 = filtered_data_2["energy_kWh"].sum()
    total_energy_shoutui = filtered_data_shoutui["energy_kWh"].sum()
    total_energy_shensuotui = filtered_data_shensuotui["energy_kWh"].sum()

    return {
        "一号推进变频器":total_energy_1,
        "二号推进变频器":total_energy_2,
        "艏推":total_energy_shoutui,
        "可伸缩推":total_energy_shensuotui,
        "总能耗":round(
            total_energy_1
            + total_energy_2
            + total_energy_shoutui
            + total_energy_shensuotui,
            2,
        ),
    }

def calculate_total_rudder_energy(start_time, end_time):
    """
    计算指定时间范围内舵桨的总能耗（单位 kWh）。

    参数：
        start_time (str): 开始时间，例如 'YYYY-MM-DD HH:MM:SS'，默认为 None（不限制）
        end_time (str): 结束时间，例如 'YYYY-MM-DD HH:MM:SS'，默认为 None（不限制）

    返回：
        dict: 舵桨的各部分能耗和总能耗，格式如下：
        {
            "一号舵桨A": total_energy_1_A,
            "一号舵桨B": total_energy_1_B,
            "二号舵桨A": total_energy_2_A,
            "二号舵桨B": total_energy_2_B,
            "总能耗": 总能耗
        }
    """

    # 文件路径和功率列名
    files_and_columns = {
        "一号舵桨A": ("database_in_use/device_1_2_meter_102.csv", "1-2-6_v"),
        "一号舵桨B": ("database_in_use/device_1_3_meter_103.csv", "1-3-6_v"),
        "二号舵桨A": ("database_in_use/device_13_2_meter_1302.csv", "13-2-6_v"),
        "二号舵桨B": ("database_in_use/device_13_3_meter_1303.csv", "13-3-6_v"),
    }

    energy_results = {}

    for rudder_name, (file_path, power_column) in files_and_columns.items():
        try:
            # 读取数据
            df = pd.read_csv(file_path)

            # 确保时间列是 datetime 格式
            df["csvTime"] = pd.to_datetime(df["csvTime"])

            # 筛选时间范围（如果提供）
            if start_time:
                start_time_dt = pd.to_datetime(start_time)
                df = df[df["csvTime"] >= start_time_dt]
            if end_time:
                end_time_dt = pd.to_datetime(end_time)
                df = df[df["csvTime"] < end_time_dt]

            if df.empty:
                energy_results[rudder_name] = 0.00
                continue  # 如果数据为空，跳过这个文件

            # 计算时间间隔（分钟 → 小时）
            df["time_diff_hours"] = 1 / 60  # 1 分钟 = 1/60 小时

            # 计算当前文件的总能耗（kWh）
            df["Energy_kWh"] = df[power_column] * df["time_diff_hours"]
            total_energy = df["Energy_kWh"].sum()

            # 记录到字典
            energy_results[rudder_name] = round(total_energy, 2)

        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            energy_results[rudder_name] = 0.00  # 文件缺失时，能耗记为 0

    # 计算总能耗
    energy_results["总能耗"] = round(sum(energy_results.values()), 2)

    return energy_results

def get_device_status_by_time_range(start_time, end_time, device_name):
    """
    根据数据表名、开始时间和结束时间，查询某个设备在该时间段内的状态变化，并排除 status 为 'False' 的记录。
    参数:
    start_time (str): 开始时间，格式为 'YYYY-MM-DD HH:MM:SS'
    end_time (str): 结束时间，格式为 'YYYY-MM-DD HH:MM:SS'
    device_name (str): 设备名称，可选值为 'A架'、'折臂吊车'、'定位设备'

    返回:
    dict: 包含设备状态变化的时间点和对应状态的字典，或错误信息
    """

    def get_status_changes(table_name, device_name):
        """
        辅助函数：获取指定设备在指定时间范围内的状态变化。

        参数:
        table_name (str): 数据表名
        device_name (str): 设备名称

        返回:
        dict: 包含设备状态变化的时间点和对应状态的字典，或错误信息
        """
        metadata = {
            "table_name": table_name,
            "start_time": start_time,
            "end_time": end_time,
        }

        try:
            df = pd.read_csv(f"database_in_use/{table_name}.csv")
        except FileNotFoundError:
            return {"error": f"数据表 {table_name} 不存在", "metadata": metadata}

        # 将csvTime列从时间戳转换为datetime类型
        df["csvTime"] = pd.to_datetime(df["csvTime"], unit="ns")  # 假设时间戳是纳秒级别

        # 将开始时间和结束时间转换为datetime类型
        start_time_dt = pd.to_datetime(start_time)
        end_time_dt = pd.to_datetime(end_time)

        # 筛选指定时间范围内的数据，并排除 status 为 'False' 的记录
        filtered_data = df[
            (df["csvTime"] >= start_time_dt)
            & (df["csvTime"] <= end_time_dt)
            & (df["status"] != "False")
        ]

        if filtered_data.empty:
            return {
                "error": f"在数据表 {table_name} 中未找到时间范围 {start_time} 到 {end_time} 且 status 不为 'False' 的数据",
                "metadata": metadata,
            }

        # 检查是否存在status列
        if "status" not in filtered_data.columns:
            return {
                "error": f"数据表 {table_name} 中不存在 'status' 列",
                "metadata": metadata,
            }

        # 获取设备状态变化的时间点和对应状态
        status_changes = filtered_data[
            ["csvTime", "status"]
        ].copy()  # 显式创建副本以避免警告

        # 使用 .loc 避免 SettingWithCopyWarning
        status_changes.loc[:, "csvTime"] = status_changes["csvTime"].dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 将结果转换为字典
        return {
            "设备名称": device_name,
            "正在进行的关键动作": status_changes.to_dict(orient="records"),
        }

    # 获取三个设备的状态变化
    if device_name == "A架":
        results = get_status_changes("Ajia_plc_1", "A架")
    if device_name == "折臂吊车":
        results = get_status_changes("device_13_11_meter_1311", "折臂吊车")
    if device_name == "定位设备":
        results = get_status_changes("Port3_ksbg_9", "定位设备")

    # # 过滤掉包含错误的结果
    # results = [
    #     result for result in results if "error" not in result
    # ]

    # # 返回结果和元数据
    # return {
    #     "result": results,
    #     "metadata": {"start_time": start_time, "end_time": end_time},
    # }
    return results


def calculate_generator_energy_consumption(start_time, end_time):
    """
    计算指定时间范围内四个发电机的能耗与总能耗。
    Parameters:
        start_time (datetime): 要计算能耗的时间段的开始时间。
        end_time (datetime): 要计算能耗的时间段的结束时间。
    Returns:
        dict: 包含四个发电机的能耗和总能耗（kWh）的字典，如果数据为空则返回 None。
    """
    file_path_1 = "database_in_use/Port1_ksbg_3.csv"
    power_column_1 = "P1_66"  # 一号发电机功率,单位:kW

    file_path_2 = "database_in_use/Port1_ksbg_3.csv"
    power_column_2 = "P1_75"  # 二号发电机功率,单位:kW

    file_path_3 = "database_in_use/Port2_ksbg_2.csv"
    power_column_3 = "P2_51"  # 三号发电机功率,单位:kW

    file_path_4 = "database_in_use/Port2_ksbg_3.csv"
    power_column_4 = "P2_60"  # 四号发电机功率,单位:kW

    try:
        # 加载 CSV 文件
        df1 = pd.read_csv(file_path_1)
        df2 = pd.read_csv(file_path_2)
        df3 = pd.read_csv(file_path_3)
        df4 = pd.read_csv(file_path_4)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"文件未找到: {e}")

    # 确保时间列是 datetime 类型
    try:
        df1["csvTime"] = pd.to_datetime(df1["csvTime"])
        df2["csvTime"] = pd.to_datetime(df2["csvTime"])
        df3["csvTime"] = pd.to_datetime(df3["csvTime"])
        df4["csvTime"] = pd.to_datetime(df4["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    # 筛选特定时间范围内的数据
    filtered_data_1 = df1[
        (df1["csvTime"] >= start_time) & (df1["csvTime"] < end_time)
    ].copy()
    filtered_data_2 = df2[
        (df2["csvTime"] >= start_time) & (df2["csvTime"] < end_time)
    ].copy()
    filtered_data_3 = df3[
        (df3["csvTime"] >= start_time) & (df3["csvTime"] < end_time)
    ].copy()
    filtered_data_4 = df4[
        (df4["csvTime"] >= start_time) & (df4["csvTime"] < end_time)
    ].copy()

    if (
        filtered_data_1.empty
        or filtered_data_2.empty
        or filtered_data_3.empty
        or filtered_data_4.empty
    ):
        return None

    # 计算时间差（秒）
    filtered_data_1.loc[:, "diff_seconds"] = (
        filtered_data_1["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_2.loc[:, "diff_seconds"] = (
        filtered_data_2["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_3.loc[:, "diff_seconds"] = (
        filtered_data_3["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_4.loc[:, "diff_seconds"] = (
        filtered_data_4["csvTime"].diff().dt.total_seconds().shift(-1)
    )

    # 计算每个时间间隔的能耗（kWh）
    filtered_data_1.loc[:, "energy_kWh"] = (
        filtered_data_1["diff_seconds"] * filtered_data_1[power_column_1] / 3600
    )
    filtered_data_2.loc[:, "energy_kWh"] = (
        filtered_data_2["diff_seconds"] * filtered_data_2[power_column_2] / 3600
    )
    filtered_data_3.loc[:, "energy_kWh"] = (
        filtered_data_3["diff_seconds"] * filtered_data_3[power_column_3] / 3600
    )
    filtered_data_4.loc[:, "energy_kWh"] = (
        filtered_data_4["diff_seconds"] * filtered_data_4[power_column_4] / 3600
    )

    # 计算总能耗
    total_energy_1 = filtered_data_1["energy_kWh"].sum()
    total_energy_2 = filtered_data_2["energy_kWh"].sum()
    total_energy_3 = filtered_data_3["energy_kWh"].sum()
    total_energy_4 = filtered_data_4["energy_kWh"].sum()

    return {
        "一号发电机":total_energy_1,
        "二号发电机":total_energy_2,
        "三号发电机":total_energy_3,
        "四号发电机":total_energy_4,
        "总能耗":round(total_energy_1 + total_energy_2 + total_energy_3 + total_energy_4, 2),
    }


def check_ajia_angle(start_time, end_time):
    """
    检查在指定时间范围内的 A 架角度异常数据。
    Params:
        start_time (datetime): 起始时间。
        end_time (datetime): 结束时间。
    Returns:
        list: 包含异常时间段的元组列表，每个元组包含异常开始时间和结束时间。如果没有异常数据，返回 None。
    Exceptions:
        FileNotFoundError: 如果 CSV 文件未找到。
        ValueError: 如果时间列转换失败。
    """
    file_path = "database_in_use/Ajia_plc_1.csv"

    # 读取 CSV 文件
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {file_path} 未找到")

    # 确保时间列是 datetime 类型
    try:
        df["csvTime"] = pd.to_datetime(df["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    # 筛选特定时间范围内的数据
    filtered_data: pd.DataFrame = df[
        (df["csvTime"] >= start_time) & (df["csvTime"] < end_time)
    ].copy()

    # 检查数据是否存在
    if filtered_data.empty:
        print(f"在时间范围 {start_time} 到 {end_time} 未找到数据")
        return None

    error_time = []
    error_status = False
    error_start_time = ""
    error_end_time = ""
    for index, row in filtered_data.iterrows():
        if row["Ajia-0_v"] == "error" or row["Ajia-1_v"] == "error":
            if not error_status:
                continue
            else:
                error_end_time = filtered_data.loc[index - 1, "csvTime"]
                print("A架角度异常数据结束：", error_end_time)
                error_time.append((error_start_time, error_end_time))
                error_status = False
                continue
        if abs(float(row["Ajia-0_v"]) - float(row["Ajia-1_v"])) > 5:
            if not error_status:
                error_status = True
                error_start_time = row["csvTime"]
                print("A架角度异常数据开始：", error_start_time)
        else:
            if error_status:
                error_end_time = filtered_data.loc[index - 1, "csvTime"]
                print("A架角度异常数据结束：", error_end_time)
                error_time.append((error_start_time, error_end_time))
                error_status = False
    print("A架角度异常数据时间段：", error_time)
    return error_time


def calculate_fuel_consumption(start_time, end_time):
    """
    计算给定时间范围内四个发动机组的燃油消耗量，以及总和。
    Args:
        start_time (datetime): 要计算燃油消耗的时间段的开始时间。
        end_time (datetime): 要计算燃油消耗的时间段的结束时间。
    Returns:
        dict: 包含四个发动机组的燃油消耗量和总燃油消耗量（L）的字典，如果数据为空则返回 None。
    Raises:
        FileNotFoundError: 如果 CSV 文件未找到。
        ValueError: 如果时间列转换失败。
    """
    file_path_1 = "database_in_use/Port1_ksbg_1.csv"
    fuel_column_1 = "P1_3"  # 一号发动机燃油消耗,单位:L/h

    file_path_2 = "database_in_use/Port1_ksbg_1.csv"
    fuel_column_2 = "P1_25"  # 二号发动机燃油消耗,单位:L/h

    file_path_3 = "database_in_use/Port2_ksbg_1.csv"
    fuel_column_3 = "P2_3"  # 三号发动机燃油消耗,单位:L/h

    file_path_4 = "database_in_use/Port2_ksbg_1.csv"
    fuel_column_4 = "P2_25"  # 四号发动机燃油消耗,单位:L/h

    try:
        # 加载 CSV 文件
        df1 = pd.read_csv(file_path_1)
        df2 = pd.read_csv(file_path_2)
        df3 = pd.read_csv(file_path_3)
        df4 = pd.read_csv(file_path_4)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"文件未找到: {e}")

    # 确保时间列是 datetime 类型
    try:
        df1["csvTime"] = pd.to_datetime(df1["csvTime"])
        df2["csvTime"] = pd.to_datetime(df2["csvTime"])
        df3["csvTime"] = pd.to_datetime(df3["csvTime"])
        df4["csvTime"] = pd.to_datetime(df4["csvTime"])
    except Exception as e:
        raise ValueError(f"时间列转换失败: {e}")

    # 筛选特定时间范围内的数据
    filtered_data_1: pd.DataFrame = df1[
        (df1["csvTime"] >= start_time) & (df1["csvTime"] < end_time)
    ].copy()
    filtered_data_2: pd.DataFrame = df2[
        (df2["csvTime"] >= start_time) & (df2["csvTime"] < end_time)
    ].copy()
    filtered_data_3: pd.DataFrame = df3[
        (df3["csvTime"] >= start_time) & (df3["csvTime"] < end_time)
    ].copy()
    filtered_data_4: pd.DataFrame = df4[
        (df4["csvTime"] >= start_time) & (df4["csvTime"] < end_time)
    ].copy()

    if (
        filtered_data_1.empty
        or filtered_data_2.empty
        or filtered_data_3.empty
        or filtered_data_4.empty
    ):
        return None

    # 计算时间差（秒）
    filtered_data_1.loc[:, "diff_seconds"] = (
        filtered_data_1["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_2.loc[:, "diff_seconds"] = (
        filtered_data_2["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_3.loc[:, "diff_seconds"] = (
        filtered_data_3["csvTime"].diff().dt.total_seconds().shift(-1)
    )
    filtered_data_4.loc[:, "diff_seconds"] = (
        filtered_data_4["csvTime"].diff().dt.total_seconds().shift(-1)
    )

    # 计算每个时间间隔的燃油消耗（L）
    filtered_data_1.loc[:, "fuel_L"] = (
        filtered_data_1["diff_seconds"] * filtered_data_1[fuel_column_1] / 3600
    )
    filtered_data_2.loc[:, "fuel_L"] = (
        filtered_data_2["diff_seconds"] * filtered_data_2[fuel_column_2] / 3600
    )
    filtered_data_3.loc[:, "fuel_L"] = (
        filtered_data_3["diff_seconds"] * filtered_data_3[fuel_column_3] / 3600
    )
    filtered_data_4.loc[:, "fuel_L"] = (
        filtered_data_4["diff_seconds"] * filtered_data_4[fuel_column_4] / 3600
    )

    # 计算总燃油消耗量
    total_fuel_1 = filtered_data_1["fuel_L"].sum()
    total_fuel_2 = filtered_data_2["fuel_L"].sum()
    total_fuel_3 = filtered_data_3["fuel_L"].sum()
    total_fuel_4 = filtered_data_4["fuel_L"].sum()

    return {
        "一号发电机":total_fuel_1,
        "二号发电机":total_fuel_2,
        "三号发电机":total_fuel_3,
        "四号发电机":total_fuel_4,
        "总燃油消耗量":round(total_fuel_1 + total_fuel_2 + total_fuel_3 + total_fuel_4, 2),
    }


def calculate_percent(a, b):
    """
    计算a占b的百分比。
    Args:
        a (float): 被除数。
        b (float): 除数。
    Returns:
        float: a占b的百分比，若b为0则返回0。
    """
    if b == 0:
        return 0
    return round(a / b * 100, 2)


def calculate_theoretical_energy_output(consumption, density, heating_value):
    """
    计算理论发电量。
    Args:
        consumption (float): 燃油消耗量（L）。
        density (float): 燃油密度（kg/L）。
        heating_value (float): 燃油热值（MJ/kg）。
    Returns:
        float: 理论发电量（kWh）。
    """
    # 计算燃油质量（kg）
    mass = consumption * density

    # 计算理论发电量（kWh）
    energy = mass * heating_value / 3.6

    return round(energy, 2)


def get_field_dict():
    """
    获取字段字典。

    Returns:
        dict: 包含字段名和字段中文名的字典。
    """
    return field_dict

def sum_list(ls):
    """
    计算列表元素之和。
    Args:
        ls (list): 要计算的列表。
    Returns:
        float: 列表元素之和。
    """
    return round(sum(ls), 2)

def get_work_time(start_time, end_time):
    """
    计算指定时间范围内的作业时间。
    Args:
        start_time (str): 要查询设备状态的时间范围的开始时间。
        end_time (str): 要查询设备状态的时间范围的结束时间。
    Returns:
        list of dict: 包含作业开始时间和结束时间的字典列表。
    """
    action_ajia = get_device_status_by_time_range(start_time, end_time, "A架")["正在进行的关键动作"]
    action_dp = get_device_status_by_time_range(start_time, end_time, "定位设备")["正在进行的关键动作"]

    action_ajia = [action for action in action_ajia if action["status"] == "开机" or action["status"] == "关机"]
    action_dp = [action for action in action_dp if action["status"] == "ON_DP" or action["status"] == "OFF_DP"]

    time_section = []
    start = None
    end = None
    for action in action_ajia:
        if action["status"] == "开机":
            start = action["csvTime"]
        if action["status"] == "关机":
            end = action["csvTime"]
            time_section.append((start, end))
            start = None
            end = None
    for action in action_dp:
        if action["status"] == "ON_DP":
            start = action["csvTime"]
        if action["status"] == "OFF_DP":
            end = action["csvTime"]
            time_section.append((start, end))
            start = None
            end = None

    time_section.sort(key=lambda x: x[0])

    merged_time_section = []
    current_start, current_end = time_section[0]
    for start, end in time_section[1:]:
        if start <= current_end:  # 如果当前时间片段与下一个时间片段重叠或相邻
            current_end = max(current_end, end)  # 合并时间片段
        else:
            merged_time_section.append({"作业开始": current_start, "作业结束":current_end})  # 保存当前合并后的时间片段
            current_start, current_end = start, end  # 开始新的时间片段

    # 添加最后一个合并后的时间片段
    merged_time_section.append({"作业开始": current_start, "作业结束":current_end})

    return merged_time_section


def find_missing_records(table_name: str, start_time, end_time):
    # 读取 CSV 文件
    df = pd.read_csv("./database_in_use/" + table_name, parse_dates=['csvTime'])

    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # 确保时间格式为 年-月-日 时:分
    df['csvTime'] = df['csvTime'].dt.strftime('%Y-%m-%d %H:%M')

    # 生成完整的时间范围
    full_time_range = pd.date_range(start=start_time, end=end_time, freq='T').strftime('%Y-%m-%d %H:%M')

    # 现有数据的时间集合
    existing_times = set(df['csvTime'])

    # 找到缺失的时间点
    missing_times = [t for t in full_time_range if t not in existing_times]

    # 返回字典
    return {
        "missing_count": len(missing_times),
        "missing_present": len(missing_times) / len(full_time_range)
    }


def count_oscillations(start_time, end_time, name: str, angle_range_start, angle_range_end):

    # 读取 CSV 文件
    df = pd.read_csv("./database_in_use/" + "Ajia_plc_1" + ".csv", parse_dates=['csvTime'])

    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    # 选择正确的角度字段
    angle_column = "Ajia-1_v" if name == "左舷" else "Ajia-0_v"

    # 过滤时间范围内的数据
    df = df[(df['csvTime'] >= start_time) & (df['csvTime'] <= end_time)]

    # 转换角度列为浮点数
    df[angle_column] = pd.to_numeric(df[angle_column], errors='coerce')

    # 获取角度数据
    angles = df[angle_column].dropna().values

    # 计算摆动次数
    oscillation_count = 0
    in_range = False

    for angle in angles:
        if angle_range_start <= angle <= angle_range_end:
            if not in_range:
                oscillation_count += 1
                in_range = True
        else:
            in_range = False

    return {"count": oscillation_count}


# def calculate_before_time_percent(actions, status, time):
#     num = 0
#     selected = 0
#     for action in actions:
#         if action["status"] == status:
#             num += 1
#             if action["time"]

if __name__ == "__main__":
    print(find_missing_records("Jiaoche_plc_1", "2024-05-20 00:00:00", "2024-05-25 00:00:00"))
