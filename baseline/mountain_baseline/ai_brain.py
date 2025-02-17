import json
from zhipuai import ZhipuAI
import tools
import api
import os

folders = ["database_in_use", "data"]
if any(not os.path.exists(folder) for folder in folders):
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    import data_process # for data process using
else:
    print("所有文件夹均已存在。不再重新预处理数据。")
    print("需要预处理数据，请删除文件夹后重新运行。")


def create_chat_completion(messages, model="glm-4-plus"):
    print("发起AI对话")
    client = ZhipuAI(api_key="6cf617672cae4afa9a280657a87beccb.m5ii3yJ1p3E42abg")
    response = client.chat.completions.create(
        model=model, stream=False, messages=messages
    )
    print("AI回复:", response.choices[0].message)
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
        print("尝试次数：", attempt)
        print("AI回复:", response.choices[0].message)
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
}


def get_answer_2(question, tools, api_look: bool = True):
    filtered_tools = tools
    try:
        messages = [
            {
                "role": "system",
                "content": 
                "你是深远海船舶设备数据分析专家，能够使用用户提供的函数来回答问题。不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息。你的回答应该尽可能使用自然语言描述，减少使用结构化的数据，省略数值计算的过程。",
            },
            {"role": "user", "content": question},
        ]
        # 第一次调用模型
        response = glm4_create(6, messages, filtered_tools)
        messages.append(response.choices[0].message.model_dump())
        print("更新后的messages:", messages)
        function_results = []
        # 最大迭代次数
        max_iterations = 6
        for _ in range(max_iterations):
            if not response.choices[0].message.tool_calls:
                break

            for tool_call in response.choices[0].message.tool_calls:
                # 获取工具调用信息
                print("tool_call:", tool_call)
                args = json.loads(tool_call.function.arguments)
                function_name = tool_call.function.name

                # 执行工具函数
                if function_name in function_map:
                    print(f"执行工具函数: {function_name}，参数: {args}")
                    function_result = function_map[function_name](**args)
                    print(f"工具函数执行结果: {function_result}")

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
            print("更新后的messages:", messages)
            response = glm4_create(8, messages, filtered_tools)
        return response.choices[0].message.content, str(function_results)
    except Exception as e:
        print(f"Error generating answer for question: {question}, {e}")
        return None, None

def select_api_based_on_question(question, tools):
    # 根据问题内容选择相应的 API
    if "甲板机械设备" in question and "能耗" in question:
        print("问题包含：甲板机械设备、能耗")
        print("提供Api：calculate_total_deck_machinery_energy")
        api_list_filter = ["calculate_total_deck_machinery_energy"]
    elif "总能耗" in question:
        print("问题包含：总能耗")
        print("提供Api：calculate_total_energy")
        api_list_filter = ["calculate_total_energy"]
    elif "动作" in question:
        print("问题包含：动作")
        print("提供Api：get_device_status_by_time_range")
        api_list_filter = ["get_device_status_by_time_range"]
        question = question + "动作直接引用不要修改,如【A架摆回】"
    elif "开机时长" in question:
        print("问题包含：开机时长")
        print("提供Api：calculate_uptime")
        api_list_filter = ["calculate_uptime"]
        if "运行时长" in question:
            question = question.replace("运行时长", "开机时长")
    elif "运行时长" in question and "实际运行时长" not in question:
        print("问题包含：运行时长，不包含：实际运行时长")
        print("提供Api：calculate_uptime")
        api_list_filter = ["calculate_uptime"]
        question = question.replace("运行时长", "开机时长")
    else:
        print("根据表名选择 Api")
        # 如果问题不匹配上述条件，则根据表名选择 API
        table_name_string = choose_table(question)
        with open("dict.json", "r", encoding="utf-8") as file:
            table_data = json.load(file)
        table_name = [
            item for item in table_data if item["数据表名"] in table_name_string
        ]

        if "设备参数详情表" in [item["数据表名"] for item in table_name]:
            print("使用设备参数详情表")
            print("提供Api：query_device_parameter")
            api_list_filter = ["query_device_parameter"]
            content_p_1 = str(table_name) + question  # 补充 content_p_1
        else:
            print("使用数据表")
            print("提供Api：get_table_data")
            api_list_filter = ["get_table_data"]
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


def enhanced(prompt, context=None, instructions=None, modifiers=None):
    """
    增强提示词函数
    """
    enhanced_prompt = prompt.replace("XX小时XX分钟", "XX小时XX分钟，01小时01分钟格式")
    enhanced_prompt = prompt.replace("发生了什么", "什么设备在进行什么动作，动作直接引用不要修改,如【A架摆回】")
    enhanced_prompt = prompt.replace("什么设备进行了什么关键动作", "什么设备进行了什么关键动作（列举所有进行了某个动作的设备）")
    enhanced_prompt = prompt.replace("运行的平均时间", "运行的平均时间（每天运行时长的平均值）")
    print("增强提示词：", enhanced_prompt)
    return enhanced_prompt

def run_conversation_xietong(question):
    question = enhanced(question)
    content_p_1, filtered_tool = select_api_based_on_question(
        question, tools.tools_all
    ) 
    print("content_p_1:", content_p_1)
    print("filtered_tool:", filtered_tool)
    answer, select_result = get_answer_2(
        question=content_p_1, tools=filtered_tool, api_look=False
    )
    return answer

def get_answer(question):
    try:
        print(f"尝试解决问题：{question}")
        last_answer = run_conversation_xietong(question)
        last_answer = last_answer.replace(" ", "")
        return last_answer
    except Exception as e:
        print(f"Error occurred while executing get_answer: {e}")
        return "An error occurred while retrieving the answer."

if __name__ == "__main__":
    question = "2024/8/23 和 2024/8/24 上午A架运行的平均时间多少（四舍五入至整数分钟输出）"
    aa = get_answer(question)
    print("*******************最终答案***********************")
    print(aa)
