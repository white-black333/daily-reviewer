import requests
from bs4 import BeautifulSoup

def web_fetcher_node(state):
    """
    Node: Fetches content from URLs requested by the DeepAgent.
    This supports 'Recursive Inquiry' (agent asking "what is this link?").
    """
    print("--- 正在抓取补充网页信息 ---")
    
    urls_to_fetch = state.get("urls_to_fetch", [])
    if not urls_to_fetch:
        return {"data_list": state.get("data_list", [])}
        
    fetched_results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for url in urls_to_fetch:
        try:
            print(f"  -> Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title and meta description
                title = soup.title.string.strip() if soup.title else "No Title"
                meta_desc = ""
                meta = soup.find("meta", attrs={"name": "description"})
                if meta:
                    meta_desc = meta.get("content", "").strip()
                
                # Extract main text (simple heuristic: p tags)
                p_texts = [p.get_text().strip() for p in soup.find_all('p')]
                content_summary = " ".join(p_texts)[:1000] # Limit to 1000 chars to save context
                
                fetched_results.append({
                    "source": "web_fetch",
                    "url": url,
                    "title": title,
                    "description": meta_desc,
                    "content_snippet": content_summary
                })
            else:
                fetched_results.append({"source": "web_fetch", "url": url, "error": f"Status {response.status_code}"})
                
        except Exception as e:
            fetched_results.append({"source": "web_fetch", "url": url, "error": str(e)})
            
    # Remove the request from state to prevent infinite loops if we were to re-run
    # But in the graph, we usually just append to data_list.
    
    return {
        "data_list": state.get("data_list", []) + fetched_results,
        "urls_to_fetch": [] # Clear the request queue
    }
