from typing import TypedDict, List, Annotated, Optional
import operator
from langgraph.graph import StateGraph, START, END
from nodes import get_chrome_history_node, deep_agent_analysis_node, get_github_commits_node, get_todo_list_node
from nodes.web_fetcher import web_fetcher_node 
from nodes.todo_list import update_todo_node
from nodes.windows_activity import get_windows_activity_node # New node

# 定义状态流转的结构
class AgentState(TypedDict):
    data_list: Annotated[List[dict], operator.add]
    final_report: str
    # New state fields for recursion
    urls_to_fetch: Optional[List[str]]
    todo_updates: Optional[List[dict]]
    recursive_loop: bool

# 1. 初始化图
workflow = StateGraph(AgentState)

# 2. 添加节点
workflow.add_node("fetch_chrome", get_chrome_history_node)
workflow.add_node("fetch_github", get_github_commits_node)
workflow.add_node("fetch_todo", get_todo_list_node)
workflow.add_node("fetch_windows", get_windows_activity_node) # New
workflow.add_node("deep_analysis", deep_agent_analysis_node)
workflow.add_node("web_fetcher", web_fetcher_node) 
workflow.add_node("update_todo", update_todo_node) 

# 3. 建立连线 - 数据获取
workflow.add_edge(START, "fetch_chrome")
workflow.add_edge(START, "fetch_github")
workflow.add_edge(START, "fetch_todo")
workflow.add_edge(START, "fetch_windows")

workflow.add_edge("fetch_chrome", "deep_analysis")
workflow.add_edge("fetch_github", "deep_analysis")
workflow.add_edge("fetch_todo", "deep_analysis")
workflow.add_edge("fetch_windows", "deep_analysis")


# Define conditional logic
def route_after_analysis(state):
    if state.get("recursive_loop"):
        if state.get("urls_to_fetch"):
            return "web_fetcher"
        elif state.get("todo_updates"):
            return "update_todo"
    return END

workflow.add_conditional_edges(
    "deep_analysis",
    route_after_analysis,
    {
        "web_fetcher": "web_fetcher",
        "update_todo": "update_todo",
        END: END
    }
)

# Loops back to analysis
workflow.add_edge("web_fetcher", "deep_analysis")
workflow.add_edge("update_todo", "deep_analysis")

# 4. 编译并运行
app = workflow.compile()

if __name__ == "__main__":
    print("=== Daily Reviewer DeepAgent 2.0 Starting ===")
    inputs = {"data_list": []}
    # Increased recursion limit to allow for inquiries
    config = {"recursion_limit": 20}
    
    for event in app.stream(inputs, config):
        for key, value in event.items():
            if key == "deep_analysis" and "final_report" in value:
                # Only print report if it exists (might be missing during intermediate steps)
                if not value.get("recursive_loop"):
                     print("\n===== 深度审计建议 =====")
                     print(value["final_report"])
            elif key == "web_fetcher":
                print(f"  [System] Fetched {len(value.get('data_list', []))} new items")
            elif key == "update_todo":
                print(f"  [System] Todo Logic executed")
