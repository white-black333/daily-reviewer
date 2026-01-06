import sqlite3
import shutil
import os
import pandas as pd
from datetime import datetime, timedelta
from config import CHROME_HISTORY_PATH

def get_chrome_history_node(state):
    """
    节点 1: 读取当天 Chrome 浏览器历史记录
    """
    print("--- 正在获取 Chrome 历史记录 ---")
    
    history_path = CHROME_HISTORY_PATH
    temp_history = "temp_history.db"
    
    # 解耦处理：如果文件正在使用，先拷贝
    try:
        shutil.copy2(history_path, temp_history)
    except Exception as e:
        return {"data_list": [f"读取失败: {str(e)}"]}

    # 连接数据库
    conn = sqlite3.connect(temp_history)
    cursor = conn.cursor()
    
    # 查询今天凌晨到现在的数据
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Chrome 时间戳从 1601-01-01 开始计算，微秒单位
    chrome_epoch_start = (today_start - datetime(1601, 1, 1)).total_seconds() * 1000000

    query = f"""
    SELECT url, title, last_visit_time 
    FROM urls 
    WHERE last_visit_time > {chrome_epoch_start}
    ORDER BY last_visit_time DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    os.remove(temp_history) # 清理临时文件

    # 简单清洗：只取前 20 条关键记录，避免上下文过长
    history_summary = df[['title', 'url']].head(20).to_dict('records')
    
    # 将结果存入 State
    return {"data_list": history_summary}
