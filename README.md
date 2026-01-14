# Docs Q&A RAG Application

This is a RAG (Retrieval-Augmented Generation) application built with FastAPI, Streamlit, and Supabase.

## Setup

1.  **Clone the repository**
2.  **Environment Variables**
    - Copy `.env.example` to `.env`
    - Fill in `SUPABASE_URL`, `SUPABASE_KEY`, and `OPENAI_API_KEY`
3.  **Database Setup**
    - Run the SQL scripts in `sql/` in your Supabase SQL Editor:
        - `00_setup.sql` (Tables)
        - `01_match_chunks.sql` (Semantic Search RPC)
        - `02_hybrid_search.sql` (Hybrid Search RPC & Index)
4.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```
5.  **Run Backend**
    ```sh
    uvicorn backend.main:app --reload
    ```
6.  **Run Frontend**
    ```sh
    streamlit run frontend/app.py
    ```
## Configuration (Project 11)

New environment variables added for Reranking and Caching:

| Variable | Default | Description |
|----------|---------|-------------|
| `RETRIEVAL_TOP_K` | 10 | Number of candidates to retrieve. |
| `RERANK_ENABLED` | false | Enable LLM-based reranking. |
| `RERANK_TOP_N` | 5 | Number of top results to keep after reranking. |
| `CACHE_ENABLED` | false | Enable in-memory caching. |
| `CACHE_TTL_SECONDS` | 600 | Cache time-to-live in seconds. |
| `CACHE_MAX_ITEMS` | 256 | Maximum number of items in cache. |
