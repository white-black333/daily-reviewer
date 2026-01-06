import os
import re
from pathlib import Path

def get_todo_list_node(state):
    """
    节点: 读取本地 Todo.md 文件并按四象限结构化
    """
    print("--- 正在读取 Todo 列表 ---")
    
    todo_path = r"C:\Users\1\Documents\Obsidian Vault\Todo.md"
    
    try:
        if not os.path.exists(todo_path):
            return {"data_list": state.get("data_list", []) + [{"source": "todo", "error": "文件不存在"}]}
        
        with open(todo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析四象限
        quadrants = {
            "重要且紧急": [],
            "重要不紧急": [],
            "不重要但紧急": [],
            "不重要不紧急": []
        }
        
        current_quadrant = None
        lines = content.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # 识别象限标题（按从具体到一般的顺序检查）
            if line_stripped.startswith('#'):
                if '很重要' in line_stripped and '很紧急' in line_stripped:
                    current_quadrant = "重要且紧急"
                elif '不重要' in line_stripped and '不紧急' in line_stripped:
                    current_quadrant = "不重要不紧急"
                elif '不重要' in line_stripped and '紧急' in line_stripped:
                    current_quadrant = "不重要但紧急"
                elif '重要' in line_stripped and '不紧急' in line_stripped:
                    current_quadrant = "重要不紧急"
            # 提取任务项
            elif line_stripped.startswith('- [ ]') and current_quadrant:
                task = line_stripped.replace('- [ ]', '').strip()
                if task:
                    quadrants[current_quadrant].append(task)
        
        # 格式化为结构化数据
        formatted_items = []
        for quadrant, tasks in quadrants.items():
            if tasks:
                formatted_items.append({
                    "quadrant": quadrant,
                    "tasks": tasks,
                    "count": len(tasks)
                })
        
        # 将结构化的 Todo 数据添加到数据列表
        todo_data = {
            "source": "todo",
            "file_path": todo_path,
            "quadrants": formatted_items,
            "total_tasks": sum(item["count"] for item in formatted_items)
        }
        
        print(f"已解析 {todo_data['total_tasks']} 个任务，分布在 {len(formatted_items)} 个象限")
        
        return {"data_list": [todo_data]}
        
    except Exception as e:
        return {"data_list": [{"source": "todo", "error": str(e)}]}
