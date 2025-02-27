import inspect

from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from tools import *

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

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="glm-4-plus")
prompt = "You are a helpful assistant."
agent_executor = create_react_agent(llm, tools, prompt=prompt)
