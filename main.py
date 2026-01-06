from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from nodes import get_chrome_history_node, deep_agent_analysis_node, get_github_commits_node, get_todo_list_node

# 定义状态流转的结构
class AgentState(TypedDict):
    data_list: Annotated[List[dict], operator.add]  # 使用 operator.add 来合并多个节点的列表
    final_report: str

# 1. 初始化图
workflow = StateGraph(AgentState)

# 2. 添加节点
workflow.add_node("fetch_chrome", get_chrome_history_node)
workflow.add_node("fetch_github", get_github_commits_node)
workflow.add_node("fetch_todo", get_todo_list_node)
workflow.add_node("deep_analysis", deep_agent_analysis_node)

# 3. 建立连线 - 三个数据获取节点并行执行
workflow.add_edge(START, "fetch_chrome")
workflow.add_edge(START, "fetch_github")
workflow.add_edge(START, "fetch_todo")

# 三个节点都完成后，汇聚到深度分析
workflow.add_edge("fetch_chrome", "deep_analysis")
workflow.add_edge("fetch_github", "deep_analysis")
workflow.add_edge("fetch_todo", "deep_analysis")
workflow.add_edge("deep_analysis", END)

# 4. 编译并运行
app = workflow.compile()

if __name__ == "__main__":
    inputs = {"data_list": []}
    config = {"recursion_limit": 10}
    
    for event in app.stream(inputs, config):
        for key, value in event.items():
            if key == "deep_analysis":
                print("\n===== 深度审计建议 =====")
                print(value["final_report"])