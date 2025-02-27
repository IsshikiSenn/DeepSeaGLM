# NexAI深海大模型竞赛方案

- **Author**：NexAI
- **使用开源方案**：乌蒙山连着山外山

## 数据说明

### 输入数据

本方案均使用了官方提供的初赛数据，位于`raw_data`下。

### 输出数据

所有生成的中间数据和结果数据均保存在以下文件夹中：

1. `database_in_use`：处理后的数据文件。
2. `data`：临时数据文件。
3. `NexAI_result.jsonl`: 用于提交的答案文件。

### 注释文件

生成的字段注释存储在 `dict.json` 中，记录了所有数据表的字段注释信息。

---

## 目录结构

```plaintext
├── data/                       # 数据处理的中间结果
├── database_in_use/            # 处理后的数据表
├── raw_data/                   # 原始数据
├── ai_brain.py                 # 大模型API调用模块
├── api.py                      # 自定义工具函数模块
├── data_process.py             # 数据预处理脚本
├── dict.json                   # 字段注释文件
├── initial_prompt.py           # 初始提示文件
├── NexAI_result.jsonl          # 回答结果文件
├── predict_seq.py              # 序列峰值预测模块
├── question.jsonl              # 问题文件
├── README.md                   # 项目说明文件
├── requirements.txt            # 依赖文件
├── run.py                      # 主运行脚本
└── tools.py                    # 工具说明模块
```

## 快速开始

### 1.创建虚拟环境并安装依赖文件

```shell
pip install -r requirements.txt
```

### 2.运行预处理程序（可选）

项目中的数据已经处理好，如果需要重新处理数据，可以运行：

```bash
python data_process.py
```

这里会生成`dict.json`文件。

### 3.输入问题文件

将想要回答的问题保存在`question.jsonl`文件中。

### 4.运行推理程序

```bash
python run.py
```

这将会执行主函数，对`question.jsonl`中的所有问题进行回答，生成`NexAI_result.jsonl`文件。

### 5.运行单个问题（可选）

对于想要单独回答的问题，可以运行：

```bash
python ai_brain.py <问题序号>
```

这会从`question.jsonl`中读取对应序号的问题，回答后完成后会将答案保存到`NexAI_result.jsonl`中的对应位置。例如，想要回答第1个问题，可以运行：

```bash
python ai_brain.py 1
```
