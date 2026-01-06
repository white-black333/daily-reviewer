from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import LLM_MODEL, LLM_API_KEY, LLM_API_BASE

def deep_agent_analysis_node(state):
    """
    节点 2: 使用 Qwen 进行深度逻辑推理与反馈
    """
    print("--- DeepAgent 正在进行深度审计 ---")
    history_data = state.get("data_list", [])
    
    formatted_items = []
    for item in history_data:
        if "title" in item:
            visit_count = item.get('visit_count', 1)
            count_str = f" (访问{visit_count}次)" if visit_count > 1 else ""
            formatted_items.append(f"- [Chrome浏览]{count_str} {item['title']}: {item['url']}")
        elif "repo" in item:
            stats = item.get("stats", {})
            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            files_count = len(stats.get("files", []))
            formatted_items.append(
                f"- [Git提交] {item['repo']} - {item['message']} "
                f"(+{additions}/-{deletions}, {files_count}个文件) {item['url']}"
            )
        elif item.get("source") == "todo":
            for quadrant_data in item.get("quadrants", []):
                quadrant_name = quadrant_data.get("quadrant")
                tasks = quadrant_data.get("tasks", [])
                for task in tasks:
                    formatted_items.append(f"- [TODO-{quadrant_name}] {task}")
        elif "error" in item:
            formatted_items.append(f"- [错误] {item['error']}")
    
    formatted_data = "\n".join(formatted_items)

    # 初始化 Qwen 模型
    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=LLM_API_KEY,
        openai_api_base=LLM_API_BASE
    )

    system_prompt = """
    你是一个极其冷静且犀利的个人成长审计员。
    用户会提供他今日的浏览历史、GitHub 提交记录和 Todo 列表，你需要通过这些碎片信息进行『深度推理』：
    1. 心理状态分析：他是在专注工作，还是在通过碎片化信息缓解焦虑？
    2. 认知偏离警告：他的行为是否背离了高效学习的目标？
    3. Todo 执行力分析：对比 Todo 列表和实际行为，他是否在做重要的事？是否在逃避重要任务？
    4. 毒舌且精准的改进建议：不给废话，只给一针见血的行动指令。
    
    特别关注 Todo 四象限：
    - 重要且紧急的任务是否得到执行？
    - 是否在用不重要的事情逃避重要任务？
    - 浏览记录和提交记录是否与 Todo 对齐？
    
    请以"今日数字指纹审计报告"为标题。
    """

    user_content = f"以下是我今天的活动记录：\n{formatted_data}\n\n请开始你的深度审计。"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ])

    return {"final_report": response.content}
