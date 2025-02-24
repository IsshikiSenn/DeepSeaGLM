tools_all = [
    {
        "type": "function",
        "function": {
            "name": "get_table_data",
            "description": "根据数据表名、开始时间、结束时间、列名和状态获取指定时间范围内的相关数据。返回值为包含指定列名和对应值的字典。若要查询某个状态所在时间，请给出status参数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "数据表名，例如 'device_logs'。",
                    },
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "需要查询的列名列表。如果未提供，则返回所有列。",
                        "default": [],
                    },
                    "status": {
                        "type": "string",
                        "description": "需要筛选的状态（例如 '开机'、'关机'）。如果未提供，则不筛选状态。",
                        "default": "",
                    },
                },
                "required": ["table_name", "start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total_energy",
            "description": "计算指定时间段内指定设备（折臂吊车、一号门架、二号门架、绞车）的总能耗。返回值为总能耗（kWh，float 类型）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                    "device_name": {
                        "type": "string",
                        "description": "设备名称，支持以下值：'折臂吊车'、'一号门架'、'二号门架'、'绞车'",
                        "enum": ["折臂吊车", "一号门架", "二号门架", "绞车"],
                    },
                },
                "required": ["start_time", "end_time", "device_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total_deck_machinery_energy",
            "description": "计算指定时间范围内甲板机械的能耗，包括折臂吊车、一号门架、二号门架、绞车，以及总能耗。返回值为包含甲板机械四个部分（折臂吊车、一号门架、二号门架、绞车）的能耗和总能耗（kWh）的字典，如果数据为空则返回 None。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "指定时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "指定时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_device_parameter",
            "description": "通过参数中文名查询设备参数信息。返回包含参数信息的字典。",
            "parameters": {
                "type": "object",
                "properties": {
                    "parameter_name_cn": {
                        "type": "string",
                        "description": "参数中文名，用于查询设备参数信息。",
                    }
                },
                "required": ["parameter_name_cn"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_status_by_time_range",
            "description": "根据开始时间和结束时间，查询某个设备在进行什么动作。返回正在进行的设备动作。A架的动作包括关机、开机、A架摆出、缆绳挂妥、征服者出水、征服者落座、征服者起吊、征服者入水、缆绳解除、A架摆回，折臂吊车的动作包括折臂吊车关机、折臂吊车开机、小艇检查完毕、小艇入水、小艇落座，定位设备的动作包括OFF_DP和ON_DP。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                    "device_name": {
                        "type": "string",
                        "description": "设备名称，支持以下值：'A架'、'折臂吊车'、'定位设备'",
                        "enum": ["A架", "折臂吊车", "定位设备"],
                    },
                },
                "required": ["start_time", "end_time", "device_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_uptime",
            "description": "计算指定时间段内的开机时长，并返回三种格式的开机时长。设备名称支持 '折臂吊车'、'A架' 和 'DP'。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                    "shebeiname": {
                        "type": "string",
                        "enum": ["折臂吊车", "A架", "DP"],
                        "description": "设备名称，支持 '折臂吊车'、'A架' 和 'DP'，默认为 '折臂吊车'。",
                        "default": "折臂吊车",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_operational_duration",
            "description": "计算设备在指定时间段内的实际运行时长（有电流且不为0）。返回值为包含三种格式的实际运行时长的元组。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                    "device_name": {
                        "type": "string",
                        "enum": ["A架"],
                        "description": "设备名称，支持 'A架'，默认为 'A架'。",
                        "default": "A架",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total_energy_consumption",
            "description": "计算指定时间范围内推进系统的能耗，包括一号推进变频器、二号推进变频器、艏推（侧推）、可伸缩推和总能耗。返回值为包含推进系统四个部分（一号推进变频器、二号推进变频器、艏推、可伸缩推）的能耗和总能耗（kWh）的字典，如果数据为空则返回 None。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "指定时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "指定时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_generator_energy_consumption",
            "description": "计算指定时间范围内四个发电机的能耗与总能耗。返回值为包含四个发电机的能耗和总能耗（kWh）的字典，如果数据为空则返回 None。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 00:00:00'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "查询的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'，例如 '2024-08-23 12:00:00'。",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_ajia_angle",
            "description": "检查在指定时间范围内的 A 架角度异常数据。返回包含异常时间段的元组列表，每个元组包含异常开始时间和结束时间。如果没有异常数据，返回 None。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "起始时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fuel_consumption",
            "description": "计算给定时间范围内四个发动机组的燃油消耗量，以及总和。返回值为包含四个发动机组的燃油消耗量和总燃油消耗量（L）的字典，如果数据为空则返回 None。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要计算燃油消耗的时间段的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要计算燃油消耗的时间段的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_percent",
            "description": "计算a占b的百分比。返回值为a占b的百分比，若b为0则返回0。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "float",
                        "description": "被除数",
                    },
                    "b": {
                        "type": "float",
                        "description": "除数",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sum_list",
            "description": "计算列表元素之和。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ls": {
                        "type": "list",
                        "description": "要计算的列表。",
                    },
                },
                "required": ["ls"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_theoretical_energy_output",
            "description": "计算理论发电量。返回值为理论发电量（kWh）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "consumption": {
                        "type": "float",
                        "description": "燃油消耗量（L）",
                    },
                    "density": {
                        "type": "float",
                        "description": "燃油密度（kg/L）。",
                    },
                    "heating_value": {
                        "type": "float",
                        "description": "燃油热值（MJ/kg）。",
                    },
                },
                "required": ["consumption", "density", "heating_value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_field_dict",
            "description": "获取字段字典。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_work_time",
            "description": "计算指定时间范围内的作业时间。返回值为包含作业开始时间和结束时间的字典列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要查询设备状态的时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要查询设备状态的时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_missing_records",
            "description": "在指定时间范围内查找缺失的记录。返回值为字典，包含缺失记录的数量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "数据表名，例如 'Ajia_plc_1.csv'。",
                    },
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要查找缺失记录的时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要查找缺失记录的时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                },
                "required": ["start_time", "end_time"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_oscillations",
            "description": "在指定时间范围内查询A架的摆动次数。返回值为字典，包含A架摆动次数。如果是超过角度X，则摆动角度范围取(X, 999)。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要查找摆动次数的时间范围的开始时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "要查找摆动次数的时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM:SS'。",
                    },
                    "name": {
                        "type": "string",
                        "description": "用来判断摆动，输入'左舷'或'右舷'。",
                        "enum": ["左舷", "右舷"],
                    },
                    "angle_range_start": {
                        "type": "float",
                        "description": "摆动角度范围的起始值。",
                    },
                    "angle_range_end": {
                        "type": "float",
                        "description": "摆动角度范围的结束值。",
                    }
                },
                "required": ["start_time", "end_time", "name", "angle_range_start", "angle_range_end"],
            }
        }
    },
]
