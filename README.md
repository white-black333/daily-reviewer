# Daily Reviewer

A LangGraph-based workflow that analyzes your daily browser history and provides deep insights into your digital behavior patterns.

## Project Structure

```
daily_reviewer/
├── nodes/                    # Tool nodes for the workflow
│   ├── __init__.py
│   ├── chrome_history.py    # Node 1: Fetch Chrome history
│   └── deep_audit.py        # Node 2: Deep analysis with LLM
├── main.py                 # Main workflow orchestration
├── config.py                # Configuration and environment loading
├── pyproject.toml           # Project dependencies (uv)
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Features

- **Chrome History Fetching**: Automatically retrieves today's browser history
- **Deep Analysis**: Uses Qwen LLM to analyze browsing patterns and provide insights
- **Extensible Architecture**: Easy to add new tool nodes for additional analysis

## Setup

### Prerequisites

- Python 3.10+
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### Installation

```bash
uv sync
```

### Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your credentials:
   ```
   LLM_MODEL=qwen-plus
   LLM_API_KEY=your-dashscope-api-key-here
   LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
   ```

3. (Optional) Set custom Chrome history path in `.env` if needed:
   ```
   CHROME_HISTORY_PATH=/custom/path/to/chrome/history
   ```
   
   If not set, the path is auto-detected based on your OS:
   - **Windows**: `C:\Users\<YourUser>\AppData\Local\Google\Chrome\User Data\Default\History`
   - **macOS**: `~/Library/Application Support/Google/Chrome/Default/History`
   - **Linux**: `~/.config/google-chrome/Default/History`

## Usage

Run the workflow:

```bash
uv run main.py
```

The workflow will:
1. Fetch today's Chrome browser history
2. Analyze browsing patterns using Qwen LLM
3. Generate a detailed audit report with insights and recommendations

## Adding New Nodes

To add a new tool node:

1. Create a new file in `nodes/` directory
2. Define a node function that accepts `state` parameter
3. Export it in `nodes/__init__.py`
4. Add it to the workflow in `main.py`

Example:

```python
# nodes/my_tool.py
def my_analysis_node(state):
    """Your tool description"""
    result = process(state.get("data_list", []))
    return {"my_result": result}
```

Then update `main.py`:

```python
from nodes import my_analysis_node

workflow.add_node("my_tool", my_analysis_node)
workflow.add_edge("previous_node", "my_tool")
```

## Dependencies

- `langgraph`: Workflow orchestration
- `langchain`: LLM framework
- `langchain-openai`: OpenAI-compatible API integration
- `pandas`: Data processing
- `python-dotenv`: Environment variable management
- `sqlite3`: Chrome history database access

## License

MIT
