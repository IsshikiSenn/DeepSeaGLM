import asyncio
import operator
from typing import Annotated, List, Literal, Tuple, Union

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from tools import *

dotenv.load_dotenv()

tools = [
    calculate_uptime,
    compute_operational_duration,
    get_table_data,
    calculate_total_deck_machinery_energy,
    query_device_parameter,
    calculate_total_energy_consumption,
    get_device_status_by_time_range,
    calculate_generator_energy_consumption,
    check_ajia_angle,
    calculate_fuel_consumption,
    calculate_fuel_consumption_weight,
    calculate_percent,
    calculate_theoretical_energy_output,
    get_field_dict,
    sum_two,
    get_work_time,
    find_missing_records,
    find_min_value,
    find_max_value,
    find_avg_value,
    calculate_total_rudder_energy,
    count_swing_with_rule,
    count_swing_with_threshold,
    calculate_time_difference,
]

with open("dict.json", "r", encoding="utf-8") as f:
    field_dict = str(json.load(f))

# 选择agent的模型
llm = ChatOpenAI(model="glm-4-plus")
prompt = f"你是深远海船舶设备数据问答助手，根据规划好的步骤，结合使用提供的工具函数来完成其中一个步骤。你可以使用的数据表如下：{field_dict}"
agent_executor = create_react_agent(llm, tools, prompt=prompt)


class PlanExecute(TypedDict):
    """
    规划和执行的状态
    """

    input: str  # 用户问题输入
    plan: List[str]  # 规划的步骤
    past_steps: Annotated[List[Tuple], operator.add]  # 过去的步骤
    response: str  # 最终回答


class Plan(BaseModel):
    """规划的步骤"""

    steps: List[str] = Field(description="要执行的不同的步骤，按顺序排列。")


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是深远海船舶设备数据问答规划专家，能够制定解答的步骤。
深海作业分为下放（布放）阶段和回收阶段，一般一天中都会进行下放和回收。下放阶段发生在回收阶段之前，回收阶段发生在下方阶段之后，即一般下方阶段在上午，回收阶段在下午。
下方阶段的一般流程：ON_DP、A架开机、折臂吊车开机、小艇检查完毕、小艇入水、征服者起吊、征服者入水、缆绳解除、A架摆回、OFF_DP、小艇落座、折臂吊车关机、A架关机。
回收阶段的一般流程：A架开机、折臂吊车开机、A架摆出、小艇检查完毕、小艇入水、缆绳挂妥、征服者出水、征服者落座、小艇落座、折臂吊车关机、A架关机。
给出的数据表中，status列和check_current_presence列是数据预处理后生成的列，在判断数据是否异常时不需要考虑这些数据。
设备及对应数据介绍:
1. A架：A架是一种起重设备，可以在垂直甲板平面上进行摆动，主要用于深海作业设备（征服者）的发射以及回收。相关的数据：A架左/右角度、1/2号启动柜电流、一/二号门架主液压泵电流等。
2. 绞车：绞车主要用作起重、牵引和拖动。相关的数据：绞车A/B/C放缆长度/放缆速度/张力、科学变频绞车电流等。
3. 折臂吊车：折臂吊车也是一种其中设备，相对灵活。主要用于小艇的下放和回收等。相关的数据：折臂吊车液压电流/电压等。
4. 发电机组：发电机组由四台柴油发电机组以及一台应急柴油发电机组组成，是全船的电力来源。相关的数据：一/二/三/四号柴油发电机组有功功率测量/转速/燃油消耗率、应急发电机组转速/燃油消耗率。
5. 推进器：推进器包括主推进器、艏侧推以及可伸缩推。主推进器负责船舶的主要移动，几乎参与所有船舶的移动。该船一共有两个主推进器。
艏侧推是可以精确保持船头的位置，可以帮助停靠码头或者动力定位（DP）。
可伸缩推可以360°旋转，提供船舶在不同水深和不同海况条件下更加灵活的操控性。
相关的数据：一/二号推进变频器功率允许/反馈；艏推主开关电流、艏侧推螺旋桨螺距命令/反馈、艏推功率反馈/允许；伸缩推主开关电流、可伸缩推螺距命令/螺距反馈/方位命令/方位反馈/功率反馈/功率允许。
6. 舵桨：由推进器驱动，主要负责改变航向。该船有两个舵桨，每个舵桨有两个舵机。相关的数据：左/右舵桨主开关电流、一/二号舵桨转速/方向命令/反馈、一/二号舵桨转舵A/B电流等。
可供查询的数据表有：
Ajia_plc_1.csv
device_13_11_meter_1311.csv
device_13_14_meter_1314.csv
device_13_2_meter_1302.csv
device_13_3_meter_1303.csv
device_1_15_meter_115.csv
device_1_2_meter_102.csv
device_1_3_meter_103.csv
device_1_5_meter_105.csv
Jiaoche_plc_1.csv
Port1_ksbg_1.csv
Port1_ksbg_2.csv
Port1_ksbg_3.csv
Port1_ksbg_4.csv
Port1_ksbg_5.csv
Port2_ksbg_1.csv
Port2_ksbg_2.csv
Port2_ksbg_3.csv
Port2_ksbg_4.csv
Port3_ksbg_10.csv
Port3_ksbg_8.csv
Port3_ksbg_9.csv
Port4_ksbg_7.csv
Port4_ksbg_8.csv
Port4_ksbg_9.csv
设备参数详情表.csv
所有可用数据的时间范围为2024-05-16 16:00:00至2024-09-14 23:59:59。""",
        ),
        ("placeholder", "{messages}"),
    ]
)
planner = planner_prompt | ChatOpenAI(model="glm-4-plus").with_structured_output(Plan)


class Response(BaseModel):
    """返回给用户的回答"""

    response: str


class Act(BaseModel):
    """要执行的动作"""

    action: Union[Response, Plan] = Field(
        description="要执行的动作。如果你想回答用户，使用Response。如果你需要进一步使用工具来得到答案，使用Plan。"
    )


replanner_prompt = ChatPromptTemplate.from_template(
    """对于给定的问题，设计一个按步骤有序进行的计划。\
这个计划应该包括多个单独的任务，这些任务如果执行正确会产生正确的结果。不要添加任何多余的任务。\
最后一个步骤的结果应该是最终的回答。确保每一步执行前都有了必需的信息。不要跳过任何一个步骤。

你要回答的问题如下:
{input}

你原先的计划如下:
{plan}

你已经完成的步骤如下:
{past_steps}

据此更新你的计划。
如果不需要更多的步骤并且你已经可以回答用户，则按如下格式返回：
{{"response": "你的回答"}}
否则，继续设计计划。只加上还需要完成的步骤，不要加上计划中之前已经完成的步骤。按如下格式返回：
{{"steps": ["步骤1", "步骤2", "步骤3"]}}

返回结果以纯文本返回，注意不要使用\'```python\'或\'```\'！"""
)

replanner = replanner_prompt | ChatOpenAI(model="glm-4-plus").with_structured_output(
    Act
)


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""对于如下计划:
{plan_str}\n\n你要执行的是步骤{1}, {task}."""
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke(
        {
            "messages": [
                (
                    "system",
                    f'数据表中字段的说明：{field_dict}对于给定的问题，设计一个按步骤有序进行的计划，并以纯文本返回，注意不要使用\'```\'！\n这个计划应该包括多个单独的任务，这些任务如果执行正确会产生正确的结果。不要添加任何多余的任务。\n最后一个步骤的结果应该是最终的回答。确保每一步执行前都有了必需的信息。不要跳过任何一个步骤。\n你的回复必须严格按照以下格式，省略任何说明：\n{{"steps": ["步骤1", "步骤2", "步骤3"]}}',
                ),
                ("user", state["input"]),
            ]
        }
    )
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}


def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"


workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# Add a replan node
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")

# From plan we go to agent
workflow.add_edge("planner", "agent")

# From agent, we replan
workflow.add_edge("agent", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
    ["agent", END],
)

# 编译
app = workflow.compile()


async def answer():
    config = {"recursion_limit": 50}
    inputs = {
        "input": "2024/09/05 一号舵桨转舵B-电流不平衡度的最小值为多少（单位为%，四舍五入，以整数输出）？"
    }
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)


if __name__ == "__main__":
    asyncio.run(answer())
