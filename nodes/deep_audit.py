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
    
    # Remove duplicates in formatted items to avoid context window bloat
    formatted_items = list(set(formatted_items))
    formatted_data = "\n".join(formatted_items)

    # 初始化 Qwen/Claude 模型
    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=LLM_API_KEY,
        openai_api_base=LLM_API_BASE,
        temperature=0 # Use 0 for reliable JSON output
    )

    system_prompt = """
    你是一个极其冷静且犀利的个人成长审计员。现在你拥有了更强的能力：
    1. **追问 (Recursive Inquiry)**: 如果有些URL你看不懂（比如标题模糊），你可以要求去抓取内容。
    2. **自我修正 (Self-Correction)**: 如果你发现 Todo 某项任务太难导致一直拖延，你可以直接把它拆解。

    你的思考流程：
    - 阅读所有数据。
    - 发现模糊点？ -> `{"action": "fetch", "urls": ["url1"]}`
    - 发现死磕卡点？ -> `{"action": "split", "target": "Task Name", "subtasks": ["Step 1", "Step 2"]}`
    - 信息足够？ -> `{"action": "report", "content": "深度审计报告..."}`

    请严格返回 JSON 格式，不要包含 Markdown 代码块。
    JSON 示例：
    {
        "action": "fetch",
        "urls": ["http://unknown-site.com"]
    }
    或者
    {
        "action": "report",
        "content": "你的深度审计报告..."
    }
    """

    user_content = f"以下是我今天的活动记录：\n{formatted_data}\n\n请进行深度审计，如果信息不足请申请获取，如果发现需要拆解的任务请执行拆解，否则输出报告。"
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ])
        
        import json
        content = response.content.strip()
        # Handle potential markdown wrapping
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        result = json.loads(content)
        
        action = result.get("action")
        
        if action == "fetch":
            print(f"--- DeepAgent 决定追问: {result.get('urls')} ---")
            return {
                "urls_to_fetch": result.get("urls", []),
                "recursive_loop": True # Flag to continue loop
            }
            
        elif action == "split":
            print(f"--- DeepAgent 决定拆解任务: {result.get('target')} ---")
            return {
                "todo_updates": [result], # Pass the whole result as update instruction
                "recursive_loop": True
            }
            
        else:
            # Default to report
            return {
                "final_report": result.get("content", "生成报告失败"),
                "recursive_loop": False # Stop loop
            }

    except Exception as e:
        print(f"DeepAgent Error: {e}")
        # Fallback to simple reporting if JSON fails
        return {"final_report": f"审计过程出错，但在尝试分析时发生了错误: {e}", "recursive_loop": False}

