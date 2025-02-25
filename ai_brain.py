import json

from zhipuai import ZhipuAI
import traceback
import re
import Sample

import api
import tools
from initial_prompt import initial_prompt

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
    "calculate_fuel_consumption_weight": api.calculate_fuel_consumption_weight,
    "calculate_percent": api.calculate_percent,
    "calculate_theoretical_energy_output": api.calculate_theoretical_energy_output,
    "get_field_dict": api.get_field_dict,
    "sum_two": api.sum_two,
    "get_work_time": api.get_work_time,
    "find_missing_records": api.find_missing_records,
    "count_oscillations": api.count_oscillations,
    "find_min_value": api.find_min_value,
    "find_max_value": api.find_max_value,
    "find_avg_value": api.find_avg_value,
    "calculate_total_rudder_energy": api.calculate_total_rudder_energy,
    "count_swing_with_threshold": api.count_swing_with_threshold,
    "count_swing_with_rule": api.count_swing_with_rule,
    "calculate_time_difference": api.calculate_time_difference,
}


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
    现在需要回答问题：{question}。
    请结合问题描述需要查询哪些数据表。
    仅返回需要的数据表名，无需展示分析过程。
    若问题中提到A架动作,包括关机、开机、A架摆出、缆绳挂妥、征服者出水、征服者落座、征服者起吊、征服者入水、缆绳解除、A架摆回，则使用Ajia_plc_1这个数据表。
    若问题中提到折臂吊车及小艇动作,包括折臂吊车关机、折臂吊车开机、小艇检查完毕、小艇入水、小艇落座，则使用device_13_11_meter_1311这个数据表。
    """
    messages = [{"role": "user", "content": prompt}]
    response = create_chat_completion(messages)
    return str(response.choices[0].message.content)


def glm4_create(max_attempts, messages, tools=None, model="glm-4-plus"):
    print("发起AI对话")
    client = ZhipuAI(api_key="6cf617672cae4afa9a280657a87beccb.m5ii3yJ1p3E42abg")
    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        print("! 尝试次数：", attempt)
        if response.choices[0].message.content:
            print("! AI回复:", response.choices[0].message.content)
        if response.choices and response.choices[0].message:
            return response
        else:
            continue
    return response


def get_answer_2(question, tools, api_look: bool = True):
    filtered_tools = tools
    try:
        messages = [
            {
                "role": "system",
                "content": initial_prompt,
            },
            {
                "role": "user",
                "content": f"现在需要回答这个问题{question}可以使用的工具函数有{filtered_tools}请先结合提供的工具函数深度思考，详细说明如何使用以及解答思路，不需要做出最终的回答。",
            },
        ]
        # 第一次调用模型
        response = glm4_create(6, messages)
        messages.append(response.choices[0].message.model_dump())
        function_results = []
        # 最大迭代次数
        iteration = 1
        while True:
            iteration += 1
            if (
                response.choices[0].message.content
                and "已完成回答" in response.choices[0].message.content
            ):
                break

            if response.choices[0].finish_reason == "tool_calls":
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
                print(f"第{iteration}次调用模型")
                response = glm4_create(8, messages, filtered_tools)
            else:
                messages.append(response.choices[0].message.model_dump())
                messages.append(
                    {
                        "role": "user",
                        "content": "现在请使用函数完成回答。若已完成回答，请只输出'已完成回答'。否则请继续推理，若有需要则调用函数。",
                    }
                )
                print(f"第{iteration}次调用模型")
                response = glm4_create(8, messages, filtered_tools)
        messages.append(response.choices[0].message.model_dump())
        messages.append(
            {
                "role": "user",
                "content": "请根据上述回答过程，简洁地回答问题，不要分段落。注意加上数值的单位、回答格式等。",
            }
        )
        print(f"第{iteration}次调用模型")
        response = glm4_create(8, messages, filtered_tools)
        return response.choices[0].message.content, str(function_results)
    except Exception as e:
        print(f"Error generating answer for question: {question}, {e}")
        return None, None

def get_answer_in_subtask_way(question, tools, temple, api_look: bool = True):
    filtered_tools = tools
    try:
        messages = [
            {
                "role": "system",
                "content": initial_prompt,
            },
            {"role": "user", "content": question},
        ]

        # **任务拆解（CoT）**
        task_decomposition_prompt = f"""
                        你是一个智能任务拆解助手。请逐步思考，拆解成多个可执行的子任务，并确定需要调用的 API。
                        你只能使用这些工具，严格看下工具的输入与输出{[{tool['function']['name']: tool['function']['description']} for tool in filtered_tools]}。
                        这是任务分解的参考是{[{"question": one_temple["question"], "subtasks": one_temple["subtasks"]} for one_temple in temple]}
                        如果需要自我思考处理，就在api里填入"self_thought"。
                        如果需要输出，则api里填入"out_put"。
                        只需要任务分解的JSON，尽可能细致，JSON只需要step，task和api，不需要JSON的格式化标记。
                        返回 JSON的格式，格式如下：
                        {{
                            "subtasks": [
                                {{"step": 1, "task": "查询设备状态", "api": "get_device_status_by_time_range"}},
                                {{"step": 2, "task": "计算能耗", "api": "calculate_total_energy"}}
                            ]
                        }}
                        问题：{question}
                        """
        task_response = glm4_create(3, [{"role": "user", "content": task_decomposition_prompt}], [])

        def clean_json_text(text):
            # 去除 Markdown 代码块包裹（```json ... ```)
            text = re.sub(r"^```json\s*", "", text)  # 去掉开头的 ```json
            text = re.sub(r"```$", "", text)  # 去掉结尾的 ```
            return text.strip()  # 额外去掉前后空格

        clear_text = clean_json_text(task_response.choices[0].message.content)
        print("! 任务拆解结果:", clear_text)

        self_thought_memory = {"steps": []}  # 记录所有 step 的输入输出

        # 解析任务拆解结果
        task_decomposition = json.loads(clear_text)
        subtasks = task_decomposition.get("subtasks", [])

        function_results = []
        messages.append({"role": "assistant", "content": f"任务拆解: {subtasks}"})

        for subtask in subtasks:
            print(f"执行子任务 {subtask['step']}: {subtask['task']}")
            print(self_thought_memory)

            # **让 LLM 生成子任务的具体执行指令**
            subtask_prompt = f"""
                    你需要执行如下子任务：
                    {subtask["task"]}
                    你需要调用的工具是:{subtask["api"]}
                    你只需要提供参数就行，不要思考别的方法。
                    请结合 CoT 方式思考，逐步拆解执行，并调用合适的工具。
                """

            if subtask['api'] == "self_thought":
                subtask_prompt = f"""
                        你需要执行如下子任务：
                        {subtask["task"]}
                        - 你过去的任务历史（输入 & 输出）如下：
                        {json.dumps(self_thought_memory, ensure_ascii=False, indent=2, default=str)}
                        你需要结合之前的输入输出来解决这个问题，回答最好主谓宾一句话一气呵成。
                    """
            if subtask['api'] == "out_put":
                print("final")
                subtask_prompt = f"""
                        你要解决的问题是:{question}
                        你只需要通过历史记录告诉我答案，不需要调用任何工具。
                        - 你过去的任务历史（输入 & 输出）如下：
                        {json.dumps(self_thought_memory, ensure_ascii=False, indent=2, default=str)}。
                    """
            response = glm4_create(6, [{"role": "user", "content": subtask_prompt}], filtered_tools)
            messages.append(response.choices[0].message.model_dump())

            output = response.choices[0].message.model_dump()

            if not response.choices[0].message.tool_calls:
                continue  # 如果 LLM 没有调用工具，跳过

            for tool_call in response.choices[0].message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                function_name = tool_call.function.name

                if function_name in function_map:
                    print(f"! 执行工具函数: {function_name}，参数: {args}")
                    function_result = function_map[function_name](**args)

                    output = function_result

                    function_results.append(function_result)
                    messages.append({"role": "tool", "content": f"{function_result}", "tool_call_id": tool_call.id})
                else:
                    print(f"未找到对应的工具函数: {function_name}")

                # **存储 step 记录**
                self_thought_memory["steps"].append({
                    "step": subtask["step"],
                    "input": subtask["task"],
                    "output": output
                })

        # **最终总结回答**
        messages.append(
            {"role": "user", "content": "请总结所有子任务的结果，并生成最终答案。一句话尽可能详细得回答问题，不用给我过程。如果题目有输出要求，严格执行，如有单位，记得单位。"})
        final_response = glm4_create(6, messages, filtered_tools)
        return final_response.choices[0].message.content, str(function_results)
    except Exception as e:
        print(f"Error generating answer for question: {question}, {e}")
        traceback.print_exc()  # 打印完整的错误堆栈
        return None, None


def select_api_based_on_question(question, tools):

    temple = []

    api_list_filter = ["calculate_percent", "query_device_parameter", "sum_two"]
    # 根据问题内容选择相应的 API
    if "能耗" in question or "做功" in question:
        print("! 问题包含：能耗")
        if "推进" in question or "侧推" in question:
            print("! 问题包含：推进，提供Api：calculate_total_energy_consumption")
            api_list_filter.append("calculate_total_energy_consumption")
        if "甲板机械" in question or "折臂吊车" in question or "A架" in question:
            print(
                "! 问题包含：甲板机械设备，提供Api：calculate_total_deck_machinery_energy"
            )
            api_list_filter.append("calculate_total_deck_machinery_energy")
        if "发电机" in question:
            print("! 问题包含：发电机，提供Api：calculate_generator_energy_consumption")
            api_list_filter.append("calculate_generator_energy_consumption")
        if "舵桨" in question:
            print("! 问题包含：舵桨，提供Api：calculate_total_rudder_energy")
            api_list_filter.append("calculate_total_rudder_energy")
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
    if "开机时长" in question or "开机总时长" in question:
        print("! 问题包含：开机时长，供Api：calculate_uptime")
        api_list_filter.append("calculate_uptime")
    if (
        "运行时长" in question or "运行时间" in question
    ) and "实际运行时长" not in question:
        print("! 问题包含：运行时长，不包含：实际运行时长，提供Api：calculate_uptime")
        api_list_filter.append("calculate_uptime")
    if "A架" in question and "异常" in question:
        print("! 问题包含：A架、异常，提供Api：check_ajia_angle")
        api_list_filter.append("check_ajia_angle")
    if "燃油消耗量" in question:
        print(
            "! 问题包含：燃油消耗量，提供Api：calculate_fuel_consumption, calculate_fuel_consumption_weight"
        )
        api_list_filter.append("calculate_fuel_consumption")
        api_list_filter.append("calculate_fuel_consumption_weight")
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
    if "数据" in question and "缺失" in question:
        print("! 问题包含：数据、缺失，提供Api：find_missing_records")
        api_list_filter.append("find_missing_records")
        temple.append(Sample.task_temple["数据缺失"])
    if "摆动" in question and "次数" in question:
        print(
            "! 问题包含：摆动、次数，提供Api：count_swing_with_rule、count_swing_with_threshold"
        )
        api_list_filter.append("count_swing_with_rule")
        api_list_filter.append("count_swing_with_threshold")
    if "最小值" in question:
        print("! 问题包含：最小值，提供Api：find_min_value")
        api_list_filter.append("find_min_value")
    if "最大值" in question:
        print("! 问题包含：最大值，提供Api：find_max_value")
        api_list_filter.append("find_max_value")
    if "平均值" in question:
        print("! 问题包含：平均值，提供Api：find_avg_value")
        api_list_filter.append("find_avg_value")
    if "时间差" in question:
        print("! 问题包含：时间差，提供Api：calculate_time_difference")
        api_list_filter.append("calculate_time_difference")

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
        return content_p_1, filtered_tools, temple
    else:
        return question, filtered_tools, temple


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
    if "作业" in enhanced_prompt and "开始" in enhanced_prompt:
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
            enhanced_prompt
            + "（作业能耗是指深海作业A中所有发电机的能耗，应先用get_work_time列出所有作业的时间范围，再用calculate_generator_energy_consumption计算每个作业时间范围的发电机能耗，最后用sum_two计算总和。）"
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
        enhanced_prompt = (
            enhanced_prompt
            + "（DP过程是指从ON_DP到OFF_DP的过程，应先使用get_device_status_by_time_range查询所有ON_DP和OFF_DP的时间，再计算所有DP过程的能耗，最后使用sum_two函数取总和。）"
        )
    if "小艇入水到小艇落座" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（小艇入水到小艇落座是指小艇入水动作发生到小艇落座动作发生的整个时间范围，使用函数计算这段时间内的能耗时应该传入这个时间范围。）"
        )
    if "数据" in enhanced_prompt and "缺失" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（问题中给出的数据表名称可能有误，请严格按照之前给出的数据表名来查询。）"
        )
    if "从ON DP到OFF DP期间" in enhanced_prompt:
        enhanced_prompt = enhanced_prompt + "（应考虑所有ON_DP到OFF_DP的范围。）"
    if "1~4号" in enhanced_prompt:
        enhanced_prompt = enhanced_prompt + "（若问题没特别说明，则取总值）"
    if "A架的总能耗" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt + "（A架的总能耗是指一号门架和二号门架的能耗总和。）"
        )
    if "回收" in enhanced_prompt and "布放" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（深海作业分为下放（布放）阶段和回收阶段，一般下放阶段发生在回收阶段之前。）"
        )
    if "报警" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（符号'↑'表示只有在数据大于报警值时才报警，符号'↓'表示当数据小于报警值时报警。例如，题目说参数为超过160，报警值为730↑，则可能不报警，因为可能是小于730。例如，题目说参数为低于500，报警值为210↓，则可能不报警，因为可能是大于210。）"
        )
    if "开机时长" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt + "（若问题没有另外说明，开机时长以分钟为单位。）"
        )
    if "时间差" in enhanced_prompt:
        enhanced_prompt = (
            enhanced_prompt
            + "（计算时间差前先说明发生的动作以及要使用的时间，使用工具函数计算时间差时注意输入的两个时间的先后。）"
        )

    print("! 增强提示词：", enhanced_prompt)
    return enhanced_prompt


def run_conversation_xietong(question):
    question = enhanced(question)
    content_p_1, filtered_tool = select_api_based_on_question(question, tools.tools_all)
    print("content_p_1:", content_p_1)
    print("filtered_tool:", [tool["function"]["name"] for tool in filtered_tool])
    answer, select_result = get_answer_2(
        question=content_p_1, tools=filtered_tool, api_look=False
    )
    return answer


def get_answer_normal_way(question):
    try:
        print(f"! 尝试解决问题：{question}")
        last_answer = run_conversation_xietong(question)
        return last_answer
    except Exception as e:
        print(f"Error occurred while executing get_answer: {e}")
        return "An error occurred while retrieving the answer."

def get_answer_subtask_way(question):
    try:
        print(f"! 尝试解决问题：{question}")

        def run_conversation_xietong(question):
            question = enhanced(question)
            content_p_1, filtered_tool, temple = select_api_based_on_question(question, tools.tools_all)
            print("content_p_1:", content_p_1)
            print("filtered_tool:", [tool["function"]["name"] for tool in filtered_tool])
            answer, select_result = get_answer_in_subtask_way(
                question=content_p_1,
                tools=filtered_tool,
                temple=temple,
                api_look=False
            )
            return answer

        last_answer = run_conversation_xietong(question)
        return last_answer
    except Exception as e:
        print(f"Error occurred while executing get_answer: {e}")
        return "An error occurred while retrieving the answer."


if __name__ == "__main__":
    # 问题编号
    QUESTION = 100

    with open("NexAI_result.jsonl", "r", encoding="utf-8") as file:
        question_list = [json.loads(line.strip()) for line in file]
    question = question_list[QUESTION - 1]["question"]
    answer = get_answer_subtask_way(question)
    # answer = get_answer_normal_way(question)
    while not answer:
        answer = get_answer_normal_way(question)

    print("*******************最终答案***********************")
    print(answer)

    question_list[QUESTION - 1]["answer"] = answer

    with open("NexAI_result.jsonl", "w", encoding="utf-8") as file:
        for item in question_list:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")
