# Docs Q&A RAG Application

This is a RAG (Retrieval-Augmented Generation) application built with FastAPI, Streamlit, and Supabase.

## Setup

1.  **Clone the repository**
2.  **Environment Variables**
    - Copy `.env.example` to `.env`
    - Fill in `SUPABASE_URL`, `SUPABASE_KEY`, and `OPENAI_API_KEY`
3.  **Database Setup**
    - Run the SQL scripts in `sql/` in your Supabase SQL Editor.
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