from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# 加载.env文件的环境变量
load_dotenv()

# 创建一个大语言模型，model指定了大语言模型的种类
model = ChatOpenAI(model="glm-4-plus")

# 定义传递给模型的消息队列
# SystemMessage的content指定了大语言模型的身份，即他应该做什么，对他进行设定
# HumanMessage的content是我们要对大语言模型说的话，即用户的输入
messages = [
    SystemMessage(content="把下面的语句翻译为英文。"),
    HumanMessage(content="今天天气怎么样？"),
]

# 打印模型的输出结果
print(model.invoke(messages).content)
