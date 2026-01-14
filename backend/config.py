import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # RAG Pipeline Configuration
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "10"))
    RERANK_ENABLED = os.getenv("RERANK_ENABLED", "false").lower() == "true"
    RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "5"))
    
    # Caching Configuration
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))
    CACHE_MAX_ITEMS = int(os.getenv("CACHE_MAX_ITEMS", "256"))
    
    # Index Version
    INDEX_VERSION = os.getenv("INDEX_VERSION", "v1")
    
    # Existing variables (optional helpers)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
