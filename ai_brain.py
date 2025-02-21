import json
import os

from zhipuai import ZhipuAI

import api
import tools
from initial_prompt import initial_prompt

folders = ["database_in_use", "data"]
if any(not os.path.exists(folder) for folder in folders):
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    import data_process  # for data process using
else:
    print("所有文件夹均已存在。不再重新预处理数据。")
    print("需要预处理数据，请删除文件夹后重新运行。")


def create_chat_completion(messages, model="glm-4-plus"):
    print("发起AI对话")
    client = ZhipuAI(api_key="6cf617672cae4afa9a280657a87beccb.m5ii3yJ1p3E42abg")
    response = client.chat.completions.create(
        model=model, stream=False, messages=messages
    )
    print("! AI回复:", response.choices[0].message.content)
    return response


def choose_table(question):
    print("向AI查询需要的数据表")
    with open("dict.json", "r", encoding="utf-8") as file:
        context_text = str(json.load(file))
    prompt = f"""我有如下数据表：<{context_text}>
    现在基于数据表回答问题：{question}。
    分析需要哪些数据表。
    仅返回需要的数据表名，无需展示分析过程。
    若问题中提到A架动作,包括关机、开机、A架摆出、缆绳挂妥、征服者出水、征服者落座、征服者起吊、征服者入水、缆绳解除、A架摆回，则使用Ajia_plc_1这个数据表。
    若问题中提到折臂吊车及小艇动作,包括折臂吊车关机、折臂吊车开机、小艇检查完毕、小艇入水、小艇落座，则使用device_13_11_meter_1311这个数据表。
    """
    messages = [{"role": "user", "content": prompt}]
    response = create_chat_completion(messages)
    return str(response.choices[0].message.content)


def glm4_create(max_attempts, messages, tools, model="glm-4-plus"):
    print("发起AI对话")
    client = ZhipuAI(api_key="6cf617672cae4afa9a280657a87beccb.m5ii3yJ1p3E42abg")
    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        print("! 尝试次数：", attempt)
        print("! AI回复:", response.choices[0].message.content)
        if (
            response.choices
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            if "```python" in response.choices[0].message.content:
                # 如果结果包含字符串'python'，则继续下一次循环
                continue
            else:
                # 一旦结果不包含字符串'python'，则停止尝试
                break
        else:
            return response
    return response


function_map = {
    "calculate_uptime": api.calculate_uptime,
    "compute_operational_duration": api.compute_operational_duration,
    "get_table_data": api.get_table_data,
    "load_and_filter_data": api.load_and_filter_data,
    "calculate_total_energy": api.calculate_total_energy,
    "calculate_total_deck_machinery_energy": api.calculate_total_deck_machinery_energy,
    "query_device_parameter": api.query_device_parameter,
    "get_device_status_by_time_range": api.get_device_status_by_time_range,
    "calculate_total_energy_consumption": api.calculate_total_energy_consumption,
    "calculate_generator_energy_consumption": api.calculate_generator_energy_consumption,
    "check_ajia_angle": api.check_ajia_angle,
    "calculate_fuel_consumption": api.calculate_fuel_consumption,
    "calculate_percent": api.calculate_percent,
    "calculate_theoretical_energy_output": api.calculate_theoretical_energy_output,
    "get_field_dict": api.get_field_dict,
    "sum_list": api.sum_list,
    "get_work_time": api.get_work_time,
}


def get_answer_2(question, tools, api_look: bool = True):
    filtered_tools = tools
    try:
        messages = [
            {
                "role": "system",
                "content": initial_prompt,
            },
            {"role": "user", "content": question},
        ]
        # 第一次调用模型
        response = glm4_create(6, messages, filtered_tools)
        messages.append(response.choices[0].message.model_dump())
        function_results = []
        # 最大迭代次数
        max_iterations = 6
        for _ in range(max_iterations):
            if not response.choices[0].message.tool_calls:
                break

            for tool_call in response.choices[0].message.tool_calls:
                # 获取工具调用信息
                print("! 调用函数:", tool_call)
                args = json.loads(tool_call.function.arguments)
                function_name = tool_call.function.name

                # 执行工具函数
                if function_name in function_map:
                    print(f"! 执行工具函数: {function_name}，参数: {args}")
                    function_result = function_map[function_name](**args)
                    print(f"! 工具函数执行结果: {function_result}")

                    function_results.append(function_result)
                    messages.append(
                        {
                            "role": "tool",
                            "content": f"{function_result}",
                            "tool_call_id": tool_call.id,
                        }
                    )
                else:
                    print(f"未找到对应的工具函数: {function_name}")
                    break
            response = glm4_create(8, messages, filtered_tools)
        messages.append(response.choices[0].message.model_dump())
        messages.append(
            {
                "role": "user",
                "content": "请根据上述回答过程，简洁地回答问题，不要分段落。",
            }
        )
        response = glm4_create(8, messages, filtered_tools)
        return response.choices[0].message.content, str(function_results)
    except Exception as e:
        print(f"Error generating answer for question: {question}, {e}")
        return None, None


def select_api_based_on_question(question, tools):
    api_list_filter = ["calculate_percent", "query_device_parameter", "sum_list"]
    # 根据问题内容选择相应的 API
    if "能耗" in question:
        print("! 问题包含：能耗，提供Api：calculate_total_energy")
        api_list_filter.append("calculate_total_energy")
        if "推进系统" in question or "侧推" in question:
            print("! 问题包含：推进系统，提供Api：calculate_total_energy_consumption")
            api_list_filter.append("calculate_total_energy_consumption")
        if "甲板机械" in question or "折臂吊车" in question:
            print(
                "! 问题包含：甲板机械设备，提供Api：calculate_total_deck_machinery_energy"
            )
            api_list_filter.append("calculate_total_deck_machinery_energy")
        if "发电机" in question:
            print("! 问题包含：发电机，提供Api：calculate_generator_energy_consumption")
            api_list_filter.append("calculate_generator_energy_consumption")
    if (
        "动作" in question
        or "DP" in question
        or "摆" in question
        or "开机" in question
        or "小艇" in question
        or "征服者" in question
        or "关机" in question
    ):
        print("! 问题包含：动作，提供Api：get_device_status_by_time_range")
        api_list_filter.append("get_device_status_by_time_range")
        question = question + "动作直接引用不要修改,如【A架摆回】"
    if "开机时长" in question:
        print("! 问题包含：开机时长，供Api：calculate_uptime")
        api_list_filter.append("calculate_uptime")
    if ("运行时长" in question or "运行时间" in question) and "实际运行时长" not in question:
        print("! 问题包含：运行时长，不包含：实际运行时长，提供Api：calculate_uptime")
        api_list_filter.append("calculate_uptime")
    if "A架" in question and "异常" in question:
        print("! 问题包含：A架、异常，提供Api：check_ajia_angle")
        api_list_filter.append("check_ajia_angle")
    if "燃油消耗量" in question:
        print("! 问题包含：燃油消耗量，提供Api：calculate_fuel_consumption")
        api_list_filter.append("calculate_fuel_consumption")
    if "发电量" in question:
        print("! 问题包含：发电量，提供Api：calculate_generator_energy_consumption")
        api_list_filter.append("calculate_generator_energy_consumption")
    if "理论发电量" in question:
        print("! 问题包含：理论发电量，提供Api：calculate_theoretical_energy_output")
        api_list_filter.append("calculate_theoretical_energy_output")
    if "字段名称" in question:
        print("! 问题包含：字段名称，提供Api：get_field_dict")
        api_list_filter.append("get_field_dict")
    if "实际运行时长" in question:
        print("! 问题包含：实际运行时长，提供Api：compute_operational_duration")
        api_list_filter.append("compute_operational_duration")
    if "作业" in question:
        print("! 问题包含：作业，提供Api：get_work_time")
        api_list_filter.append("get_work_time")

    if len(api_list_filter) == 3:
        # 如果问题不匹配上述条件，则根据表名选择 API
        table_name_string = choose_table(question)
        with open("dict.json", "r", encoding="utf-8") as file:
            table_data = json.load(file)
            table_name = [
                item for item in table_data if item["数据表名"] in table_name_string
            ]
            if "设备参数详情表" in [item["数据表名"] for item in table_name]:
                print("! 使用设备参数详情表，提供Api：query_device_parameter")
                api_list_filter.append("query_device_parameter")
                content_p_1 = str(table_name) + question  # 补充 content_p_1
            else:
                print("! 使用数据表，提供Api：get_table_data")
                api_list_filter.append("get_table_data")
                content_p_1 = str(table_name) + question

    # 过滤工具列表
    filtered_tools = [
        tool
        for tool in tools
        if tool.get("function", {}).get("name") in api_list_filter
    ]
    # 返回结果
    if "content_p_1" in locals():
        return content_p_1, filtered_tools
    else:
        return question, filtered_tools


def enhanced(prompt: str, context=None, instructions=None, modifiers=None):
    """
    增强提示词函数
    """
    enhanced_prompt = prompt
    enhanced_prompt = enhanced_prompt.replace(
        "XX小时XX分钟", "XX小时XX分钟，01小时01分钟格式"
    )
    enhanced_prompt = enhanced_prompt.replace(
        "发生了什么", "什么设备在进行什么动作，动作直接引用不要修改,如【A架摆回】"
    )
    enhanced_prompt = enhanced_prompt.replace(
        "什么设备进行了什么关键动作",
        "什么设备进行了什么关键动作（列举所有进行了某个动作的设备）",
    )
    enhanced_prompt = enhanced_prompt.replace(
        "运行的平均时间", "运行的平均时间（每天运行时长的平均值）"
    )
    if "作业" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "若问题没有特殊说明，则深海作业A的开始以ON_DP为标志，DP动作来自定位设备。"
        )
    if "A架" in enhanced_prompt and "开启" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（A架的开启时间以A架开机这个动作发生的时间为准，其他动作发生的时间不算。）"
        )
    if "A架开机" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt + "（A架开机就是“A架”这个设备发生“开机”这个动作。）"
        )
    if "发电机组" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（若问题只说发电机组，未说明是哪个发电机组，则认为是所有四个发电机组的总体值。）"
        )
    if "作业能耗" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt + "（作业能耗是指深海作业A中所有发电机的能耗，应先用get_work_time列出所有作业的时间范围，再用calculate_generator_energy_consumption计算每个作业时间范围的发电机能耗，最后用sum_list计算总和。）"
        )
    if "发电效率" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt + "（发电效率是指发电机组能耗与理论发电量的比值。）"
        )
    if "理论发电量" in enhanced_prompt:
        enhanced_prompt = enhanced_prompt + "（要计算理论发电量应先计算燃油消耗量。）"
    if "实际运行时长" in enhanced_prompt and "效率" in enhanced_prompt:
        enhanced_prompt = enhanced_prompt + "（效率是指实际运行时长和开机时长的比值。）"
    if "DP过程" in enhanced_prompt:
        enhanced_prompt = (enhanced_prompt+ "（DP过程是指从ON_DP到OFF_DP的过程，应先使用get_device_status_by_time_range查询所有ON_DP和OFF_DP的时间，再计算所有DP过程的能耗，最后使用sum_list函数取总和。）")
    if "小艇入水到小艇落座" in enhanced_prompt:
        enhanced_prompt = (enhanced_prompt+ "（小艇入水到小艇落座是指小艇入水动作发生到小艇落座动作发生的整个时间范围，使用函数计算这段时间内的能耗时应该传入这个时间范围。）")

    print("! 增强提示词：", enhanced_prompt)
    return enhanced_prompt


def run_conversation_xietong(question):
    question = enhanced(question)
    content_p_1, filtered_tool = select_api_based_on_question(question, tools.tools_all)
    print("content_p_1:", content_p_1)
    print("filtered_tool:", filtered_tool)
    answer, select_result = get_answer_2(
        question=content_p_1, tools=filtered_tool, api_look=False
    )
    return answer


def get_answer(question):
    try:
        print(f"! 尝试解决问题：{question}")
        last_answer = run_conversation_xietong(question)
        last_answer = last_answer.replace(" ", "")
        return last_answer
    except Exception as e:
        print(f"Error occurred while executing get_answer: {e}")
        return "An error occurred while retrieving the answer."


if __name__ == "__main__":
    QUESTION = 54   # 问题编号
    with open("result.jsonl", "r", encoding="utf-8") as file:
        question_list = [json.loads(line.strip()) for line in file]
    question = question_list[QUESTION - 1]["question"]
    answer = get_answer(question)
    print("*******************最终答案***********************")
    print(answer)
    question_list[QUESTION - 1]["answer"] = answer
    with open("result.jsonl", "w", encoding="utf-8") as file:
        for item in question_list:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")
