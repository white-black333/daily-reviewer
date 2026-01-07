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

def update_todo_node(state):
    """
    Node: Updates the Todo.md file based on AI instructions.
    Usually calls 'split_task' or 'mark_done' (simulated).
    """
    print("--- 正在更新 Todo 列表 ---")
    
    # In a real tool calling scenario, we would parse the tool call.
    # For this simplified version, we look for 'todo_updates' in the state.
    # Example update format: {"action": "split", "target": "Learn Rust", "subtasks": ["Read Ch1", "Install Cargo"]}
    
    updates = state.get("todo_updates", [])
    if not updates:
        return {"data_list": state.get("data_list", [])}
        
    todo_path = r"C:\Users\1\Documents\Obsidian Vault\Todo.md"
    if not os.path.exists(todo_path):
        return {"data_list": state.get("data_list", []) + [{"source": "todo_update", "error": "File not found"}]}
        
    try:
        with open(todo_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        modified = False
        
        for update in updates:
            action = update.get("action")
            target = update.get("target")
            
            if action == "split":
                subtasks = update.get("subtasks", [])
                # Simple logic: find the line with target and replace/append
                # We iterate through existing lines to rebuild
                temp_lines = []
                for line in lines:
                    if target in line and "- [ ]" in line:
                        # Keep original but maybe mark as parent? Or just replace?
                        # Let's keep original and indent subtasks
                        temp_lines.append(line)
                        indent = len(line) - len(line.lstrip())
                        base_indent = " " * (indent + 4) # Indent subtasks
                        for sub in subtasks:
                            temp_lines.append(f"{base_indent}- [ ] {sub}\n")
                        modified = True
                        print(f"  -> Splitting task '{target}' into {len(subtasks)} subtasks")
                    else:
                        temp_lines.append(line)
                lines = temp_lines # Update for next pass

        if modified:
            with open(todo_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines if new_lines else lines)
            return {"data_list": state.get("data_list", []) + [{"source": "todo_update", "status": "success"}]}
        else:
             return {"data_list": state.get("data_list", []) + [{"source": "todo_update", "status": "no_changes_needed"}]}

    except Exception as e:
        return {"data_list": state.get("data_list", []) + [{"source": "todo_update", "error": str(e)}]}

