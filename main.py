from typing import TypedDict, List, Annotated, Optional
import operator
from langgraph.graph import StateGraph, START, END
from nodes import get_chrome_history_node, deep_agent_analysis_node, get_github_commits_node, get_todo_list_node
from nodes.web_fetcher import web_fetcher_node 
from nodes.todo_list import update_todo_node
from nodes.report_renderer import render_report_node

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
workflow.add_node("deep_analysis", deep_agent_analysis_node)
workflow.add_node("web_fetcher", web_fetcher_node) 
workflow.add_node("update_todo", update_todo_node) 

# 3. 建立连线 - 数据获取
workflow.add_edge(START, "fetch_chrome")
workflow.add_edge(START, "fetch_github")
workflow.add_edge(START, "fetch_todo")

workflow.add_edge("fetch_chrome", "deep_analysis")
workflow.add_edge("fetch_github", "deep_analysis")
workflow.add_edge("fetch_todo", "deep_analysis")


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
    collected_data = []
    final_report_content = ""

    # Increased recursion limit to allow for inquiries
    config = {"recursion_limit": 50}
    
    try:
        for event in app.stream(inputs, config):
            for key, value in event.items():
                print(f"--- Node Executed: {key} ---")
                
                # Collect data from any node that produces it
                if "data_list" in value:
                    collected_data.extend(value["data_list"])
                    
                if key == "deep_analysis" and "final_report" in value:
                    # Only print report if it exists
                    if not value.get("recursive_loop"):
                         print("\n===== 深度审计建议 =====")
                         print(value["final_report"])
                         final_report_content = value["final_report"]

                elif key == "web_fetcher":
                    print(f"  [System] Fetched {len(value.get('data_list', []))} new items")
                elif key == "update_todo":
                    print(f"  [System] Todo Logic executed")
                    
    except Exception as e:
        print(f"\n[Error] Execution interrupted: {e}")
        # Try to proceed with whatever report content we have if available
        
    # Generate HTML Report
    if final_report_content:
        print("\n--- Generating HTML Report ---")
        render_state = {
            "data_list": collected_data,
            "final_report": final_report_content
        }
        render_report_node(render_state)
    elif collected_data:
        # Fallback if we have data but no report (e.g. recursion error before final report)
        print("\n--- Generating Partial HTML Report (Analysis Failed) ---")
        render_state = {
            "data_list": collected_data,
            "final_report": "### ⚠️ Analysis Incomplete\n\nThe agent encountered an error or recursion limit before completing the analysis.\n\nSee logs for details."
        }
        render_report_node(render_state)
    else:
        print("\n[Warn] No data collected, skipping report generation.")
