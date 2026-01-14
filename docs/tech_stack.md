# Стек Технологий (Tech Stack)

В данном проекте используется современный стек для построения RAG (Retrieval-Augmented Generation) приложений, ориентированный на производительность, масштабируемость и простоту разработки.

## Backend (Серверная часть)

*   **Язык**: [Python 3.9+](https://www.python.org/)
    *   Основной язык разработки в сфере AI/ML.
*   **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
    *   Высокопроизводительный асинхронный фреймворк.
    *   Автоматическая генерация Swagger UI документации.
    *   Использование Pydantic для валидации данных.
*   **Server**: [Uvicorn](https://www.uvicorn.org/)
    *   ASGI-сервер для запуска FastAPI приложения.

## Frontend (Клиентская часть)

*   **Framework**: [Streamlit](https://streamlit.io/)
    *   Python-фреймворк для быстрого создания Data Apps.
    *   Позволяет создавать интерактивный UI без знания HTML/CSS/JS.

## Database & Storage (Хранение данных)

*   **Platform**: [Supabase](https://supabase.com/)
    *   Open Source альтернатива Firebase.
*   **Database**: [PostgreSQL](https://www.postgresql.org/)
    *   Мощная реляционная СУБД.
*   **Vector Search**: [pgvector](https://github.com/pgvector/pgvector)
    *   Расширение для PostgreSQL для хранения и поиска векторов (Embeddings).
*   **Full-Text Search**: PostgreSQL FTS
    *   Встроенный движок полнотекстового поиска (используем `to_tsvector`, `websearch_to_tsquery`) и GIN индексы.
*   **RPC**: PL/pgSQL
    *   Хранимые процедуры (`match_chunks`, `match_chunks_keyword`) для выполнения логики поиска на стороне базы данных.

## AI & LLM (Искусственный Интеллект)

*   **Provider**: [OpenAI API](https://platform.openai.com/)
*   **LLM Model**: `gpt-5`
    *   Используется для генерации ответов на основе найденного контекста.
    *   Новейшая модель следующего поколения с улучшенным пониманием контекста.
*   **Embedding Model**: `text-embedding-3-small`
    *   Используется для векторизации текста (размерность 1536).

## Search Algorithms (Алгоритмы Поиска)

*   **Hybrid Search**: Объединение двух методов:
    1.  **Semantic Search** (Cosine Similarity по векторам).
    2.  **Keyword Search** (BM25-like ранжирование через `ts_rank`).
*   **RRF (Reciprocal Rank Fusion)**:
    *   Алгоритм объединения результатов из разных поисковых систем.
    *   Формула: `score = 1 / (rank + k)`, где `k=60`.
*   **Reranking**:
    *   LLM-based Listwise/Pointwise reranking.
    *   Используется для уточнения релевантности после retrieval этапа.
*   **Caching**:
    *   Custom In-memory LRU Cache (Python `OrderedDict`).
    *   TTL (Time-to-Live) инвалидация.

## DevOps & Tools

*   **Package Manager**: `pip` + `requirements.txt`
*   **Virtual Environment**: `venv`
*   **Automation**: `Make`
    *   Управление командами запуска, установки и очистки.
*   **Linting/Formatting**: Не настроено явно, рекомендуется `black` / `flake8` (опционально).
