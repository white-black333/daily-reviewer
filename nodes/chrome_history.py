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

    # 先取前 200 条记录，然后按 title 去重并统计访问次数
    if not df.empty:
        df_top = df.head(200)
        # 按 title 分组，统计访问次数，保留第一个 url
        df_grouped = df_top.groupby('title').agg({
            'url': 'first',  # 保留第一个 url
            'title': 'size'  # 统计出现次数
        }).rename(columns={'title': 'visit_count'}).reset_index()
        # 按访问次数降序排序
        df_grouped = df_grouped.sort_values('visit_count', ascending=False)
        history_summary = df_grouped.to_dict('records')
    else:
        history_summary = []
    
    # 将结果存入 State
    return {"data_list": history_summary}
