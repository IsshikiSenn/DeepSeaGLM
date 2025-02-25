task_temple = {
    "数据缺失": {
         "question": "获取表格A,B在2024-06-20到2024-06-22,缺失数据最多日期与比例分别是多少?",
         "subtasks": [
            {"step": 1, "task": "获取表格A在2024-06-20的丢失数据数量与比例", "api": "find_missing_records"},
            {"step": 2, "task": "获取表格A在2024-06-21的丢失数据数量与比例", "api": "find_missing_records"},
            {"step": 3, "task": "获取表格A在2024-06-22的丢失数据数量与比例", "api": "find_missing_records"},
            {"step": 4, "task": "获取表格B在2024-06-20的丢失数据数量与比例", "api": "find_missing_records"},
            {"step": 5, "task": "获取表格B在2024-06-21的丢失数据数量与比例", "api": "find_missing_records"},
            {"step": 6, "task": "获取表格B在2024-06-22的丢失数据数量与比例", "api": "find_missing_records"},
            {"step": 7, "task": "从历史问答中，获取表格A缺失数据最多的比例", "api": "self_thought"},
            {"step": 8, "task": "从历史问答中，获取表格B缺失数据最多的比例", "api": "self_thought"},
            {"step": 9, "task": "从历史问答中，总结并输出问题答案", "api": "out_put"}
            ]
        },
    "简单数据缺失": {
         "question": "获取表格A在2024-06-20缺失数据比例是多少?",
         "subtasks": [
            {"step": 1, "task": "获取表格A在2024-06-20的丢失数据的比例", "api": "find_missing_records"},
            {"step": 2, "task": "从历史问答中，总结并输出问题答案", "api": "out_put"}
            ]
        }
}
