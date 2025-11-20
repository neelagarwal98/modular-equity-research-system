import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")  

# Model Configuration
LLM_MODEL = "gpt-3.5-turbo"  
LLM_TEMPERATURE = 0.3  
MAX_TOKENS = 1000

# Agent Configuration
MAX_SOURCES = 5  # maximum number of URLs to analyze
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Vector Store
VECTOR_STORE_PATH = "data/vector_store"

# Confidence Thresholds
MIN_CONFIDENCE_SCORE = 0.6
HIGH_CONFIDENCE_THRESHOLD = 0.8

# Timeout Settings
MODULE_TIMEOUT = 30  # seconds
URL_LOAD_TIMEOUT = 10  # seconds

# Financial News Sources (Prioritized for equity research)
PRIORITY_DOMAINS = [
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "marketwatch.com",
    "cnbc.com",
    "fool.com",
    "seekingalpha.com",
    "yahoo.com/finance",
    "benzinga.com"
]

# Research Parameters
ENABLE_WEB_SEARCH = True
MAX_SEARCH_RESULTS = 10
