from zhipuai import ZhipuAI
from langchain.chains import TransformChain
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from tools import tools_all
import json

# 初始化智谱AI客户端
client = ZhipuAI(api_key="6cf617672cae4afa9a280657a87beccb.m5ii3yJ1p3E42abg")

# 工具调用模拟
TOOL_MAP = {tool["function"]["name"]: tool for tool in tools_all}


def tool_executor(args: dict) -> str:
    try:
        tool_name = args["tool_name"]
        params = args["params"]
        print(f"执行工具 {tool_name} 参数 {params}")
        # 这里应替换为实际工具调用
        return "计算结果示例"
    except Exception as e:
        return f"工具执行错误：{str(e)}"


# == 重新定义TransformChain ==
def decompose_chain(inputs: dict) -> dict:
    prompt = f"""请严格按JSON格式响应：
根据问题选择工具：
可用工具：{[t['function']['name'] for t in tools_all]}
问题：{inputs['prompt']}

返回格式：{{"tool": "工具名", "reason": "选择理由"}}"""
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    ).choices[0].message.content
    try:
        return json.loads(response.strip('`json').strip())
    except:
        return {"tool": "", "reason": "解析失败"}


decompose_transformer = TransformChain(
    input_variables=["prompt"],
    output_variables=["tool", "reason"],
    transform=decompose_chain,
    verbose=False
)


def params_chain(inputs: dict) -> dict:
    prompt = f"""根据工具定义提取参数（仅返回JSON）：
工具参数规范：
{inputs['tool_desc']}

问题：{inputs['input']}"""
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    ).choices[0].message.content

    try:
        params = json.loads(response.strip('`json').strip())
        return {"params": params}  # 关键修正点：确保输出包含params键
    except:
        return {"params": {}}


params_transformer = TransformChain(
    input_variables=["tool_desc", "input"],
    output_variables=["params"],
    transform=params_chain,
    verbose=False
)

# == 构建完整工作流 ==
glm_workflow = (
        RunnablePassthrough.assign(
            prompt=lambda x: x["input"]  # 将input映射到prompt
        )
        | decompose_transformer
        | {
            "tool_name": lambda x: x["tool"],
            "input": RunnablePassthrough(),  # 保持原始输入传递
            "tool_desc": lambda x: str(TOOL_MAP.get(x["tool"], {}).get('function', {}).get('parameters', '')),
            "reason": lambda x: x["reason"]
        }
        | params_transformer
        | RunnableLambda(lambda x: tool_executor({
    "tool_name": x["tool_name"],
    "params": x["params"]
}))
)

# 测试执行
result = glm_workflow.invoke({"input": "查询2024-08-23 A架摆动次数超过10度的情况"})
print("\n最终执行结果:", result)
