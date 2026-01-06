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
            formatted_items.append(f"- [Chrome浏览] {item['title']}: {item['url']}")
        elif "repo" in item:
            stats = item.get("stats", {})
            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            files_count = len(stats.get("files", []))
            formatted_items.append(
                f"- [Git提交] {item['repo']} - {item['message']} "
                f"(+{additions}/-{deletions}, {files_count}个文件) {item['url']}"
            )
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
    用户会提供他今日的浏览历史和 GitHub 提交记录，你需要通过这些碎片信息进行『深度推理』：
    1. 心理状态分析：他是在专注工作，还是在通过碎片化信息缓解焦虑？
    2. 认知偏离警告：他的行为是否背离了高效学习的目标？
    3. 毒舌且精准的改进建议：不给废话，只给一针见血的行动指令。
    请以"今日数字指纹审计报告"为标题。
    """

    user_content = f"以下是我今天的活动记录：\n{formatted_data}\n\n请开始你的深度审计。"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ])

    return {"final_report": response.content}
