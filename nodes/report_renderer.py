from datetime import datetime
import json
import os
from typing import List

def render_report_node(state):
    """
    节点: 将审计结果渲染为 HTML 报告
    """
    print("--- 正在生成 HTML 报告 ---")
    
    # 1. 准备数据
    final_report_md = state.get("final_report", "暂无报告内容")
    data_list = state.get("data_list", [])
    
    # 统计数据
    chrome_items = [item for item in data_list if "title" in item]
    github_items = [item for item in data_list if "repo" in item]
    
    chrome_count = sum([item.get('visit_count', 1) for item in chrome_items])
    github_commits = len(github_items)
    
    # Top Chrome Sites (Top 5)
    top_sites = sorted(chrome_items, key=lambda x: x.get('visit_count', 1), reverse=True)[:5]
    top_sites_html = ""
    for item in top_sites:
        title = item.get('title', 'Unknown')
        count = item.get('visit_count', 1)
        top_sites_html += f"""
            <li class="flex justify-between items-center">
                <span class="truncate w-48 text-gray-700" title="{title}">{title}</span>
                <span class="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">{count}</span>
            </li>
        """

    # 2. 读取模板
    template_path = "report_design.html"
    if not os.path.exists(template_path):
         # Try absolute path fallback
         template_path = os.path.join(os.getcwd(), "report_design.html")
         if not os.path.exists(template_path):
             return {"final_report": float("nan")} # Should ideally not return nan but for now

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. 替换内容
    js_safe_report = final_report_md.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 生成新的 script 块
    new_script = f"""
    <script>
        const SAMPLE_REPORT_MARKDOWN = `{js_safe_report}`;
        
        // Render Report
        document.getElementById('report-content').innerHTML = marked.parse(SAMPLE_REPORT_MARKDOWN);

        // Update Counts
        document.getElementById('chrome-count').textContent = "{chrome_count}";
        document.getElementById('github-count').textContent = "{github_commits}";
        
        // Update Date
        document.getElementById('current-date').textContent = "{current_date}";

        // Render Chrome List
        const chromeListEl = document.getElementById('chrome-top-list');
        chromeListEl.innerHTML = `{top_sites_html}`;
    </script>
    """
    
    # 查找特定字符串进行替换
    final_html = html_content 
    
    # 替换掉模板中的 script 区域 (简单起见，我们替换掉整个最后的 script 标签)
    # 我们的模板最后有一个 <script> 块包含了 'const SAMPLE_REPORT_MARKDOWN'
    
    split_marker = 'const SAMPLE_REPORT_MARKDOWN = `'
    if split_marker in html_content:
        # 找到 script 起始位置
        script_start = html_content.rfind('<script>')
        if script_start != -1:
             final_html = html_content[:script_start] + new_script + "</body>\n</html>"
    
        
    # 4. 保存文件
    output_filename = f"daily_report_{current_date}.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"Report generated: {output_filename}")
    # Return path so we can present it
    return {"report_path": output_filename}
