"""Configuration module for loading environment variables."""

import os
import platform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# Chrome History Path Configuration
def get_default_chrome_history_path():
    """Get default Chrome history path based on OS."""
    system = platform.system()
    if system == "Windows":
        return os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/History")
    elif system == "Linux":
        return os.path.expanduser("~/.config/google-chrome/Default/History")
    else:
        raise ValueError(f"Unsupported operating system: {system}")

CHROME_HISTORY_PATH = os.getenv("CHROME_HISTORY_PATH", get_default_chrome_history_path())

# Validate required configuration
if not LLM_API_KEY:
    raise ValueError("LLM_API_KEY environment variable is not set. Please check your .env file.")
