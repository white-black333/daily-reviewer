import requests
from datetime import datetime, timedelta
from config import GITHUB_TOKEN, GITHUB_USERNAME

def get_github_commits_node(state):
    """
    节点: 获取当天 GitHub 提交历史记录
    """
    print("--- 正在获取 GitHub 提交记录 ---")
    
    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        return {"data_list": state.get("data_list", []) + [{"error": "GitHub配置缺失"}]}
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    since_time = datetime.utcnow() - timedelta(hours=24)
    since = since_time.isoformat() + "Z"
    
    commits_summary = []
    
    try:
        repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
        repos_response = requests.get(repos_url, headers=headers, params={"per_page": 100})
        repos_response.raise_for_status()
        repos = repos_response.json()
        
        for repo in repos:
            repo_name = repo["full_name"]
            commits_url = f"https://api.github.com/repos/{repo_name}/commits"
            
            params = {
                "since": since,
                "per_page": 100
            }
            
            commits_response = requests.get(commits_url, headers=headers, params=params)
            
            if commits_response.status_code == 200:
                commits = commits_response.json()
                
                for commit in commits:
                    commit_sha = commit["sha"]
                    commit_detail_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}"
                    detail_response = requests.get(commit_detail_url, headers=headers)
                    
                    stats = {"additions": 0, "deletions": 0, "total": 0, "files": []}
                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        stats = {
                            "additions": detail.get("stats", {}).get("additions", 0),
                            "deletions": detail.get("stats", {}).get("deletions", 0),
                            "total": detail.get("stats", {}).get("total", 0),
                            "files": [f["filename"] for f in detail.get("files", [])]
                        }
                    
                    commit_data = {
                        "repo": repo_name,
                        "message": commit["commit"]["message"],
                        "sha": commit["sha"][:7],
                        "date": commit["commit"]["author"]["date"],
                        "url": commit["html_url"],
                        "stats": stats
                    }
                    commits_summary.append(commit_data)
        
        print(f"✓ 找到 {len(commits_summary)} 条今日提交记录")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ GitHub API 请求失败: {str(e)}")
        return {"data_list": state.get("data_list", []) + [{"error": f"GitHub请求失败: {str(e)}"}]}
    
    current_data = state.get("data_list", [])
    return {"data_list": current_data + commits_summary}
