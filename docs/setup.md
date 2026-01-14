# Установка и Запуск

Это руководство поможет вам развернуть проект Docs Q&A RAG на локальной машине.

## Предварительные требования

1.  **Python 3.9+**: Убедитесь, что Python установлен.
2.  **Supabase аккаунт**: Создайте проект на [supabase.com](https://supabase.com/).
3.  **OpenAI API Key**: Получите ключ на [paltform.openai.com](https://platform.openai.com/).

---

## Шаг 1: Настройка Базы Данных (Supabase)

1.  Перейдите в **SQL Editor** в панели управления вашего проекта Supabase.
2.  Выполните скрипты из папки `sql/` данного репозитория в следующем порядке:

    **А. Создание таблиц (`sql/00_setup.sql`)**
    Этот скрипт активирует расширение `vector` и создает таблицы `sources` (для файлов) и `chunks` (для фрагментов текста).

    **В. Гибридный поиск (`sql/02_hybrid_search.sql`)**
    Этот скрипт создает индекс для полнотекстового поиска и соответствующую RPC-функцию.

---

## Шаг 2: Настройка Окружения

1.  В корневой папке проекта создайте файл `.env`, скопировав пример:
    ```bash
    cp .env.example .env
    ```

2.  Откройте `.env` и заполните переменные:
    ```env
    # URL вашего проекта Supabase (Settings -> API)
    SUPABASE_URL=https://your-project-ref.supabase.co
    
    # Анонимный публичный ключ Supabase (Settings -> API -> anon public)
    SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5c...
    
    # Ваш ключ OpenAI
    OPENAI_API_KEY=sk-proj-...

    # Настройки RAG (Project 11)
    RETRIEVAL_TOP_K=10
    RERANK_ENABLED=true
    RERANK_TOP_N=5

    # Настройки Кеширования (Project 11)
    CACHE_ENABLED=true
    CACHE_TTL_SECONDS=600
    CACHE_MAX_ITEMS=256
    
    ```

---

## Шаг 3: Установка Зависимостей

Рекомендуется использовать виртуальное окружение. Вы можете использовать `make` для автоматизации:

```bash
make venv
make install
```

Либо вручную:

```bash
# Создание виртуального окружения (опционально)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Установка библиотек
pip install -r requirements.txt
```

---

---

## Шаг 4: Запуск Приложения

### Быстрый запуск (Makefile)
Если у вас установлен `make`, вы можете запустить все одной командой:
```bash
make run
```
*   API: `http://localhost:8000`
*   UI: `http://localhost:8501`

### Ручной запуск
Если вы не используете make, запустите два терминала:

#### Терминал 1: Backend (FastAPI)
Запускает API сервер.
```bash
uvicorn backend.main:app --reload
```
*   API будет доступно по адресу: `http://localhost:8000`
*   Документация Swagger UI: `http://localhost:8000/docs`

#### Терминал 2: Frontend (Streamlit)
Запускает веб-интерфейс.
```bash
streamlit run frontend/app.py
```
*   Интерфейс откроется автоматически в браузере: `http://localhost:8501`

---

## Проверка работоспособности

1.  Откройте интерфейс Streamlit.
2.  Перейдите на вкладку **Documents**.
3.  Загрузите тестовый текстовый файл.
4.  Дождитесь статуса `indexed`.
5.  Перейдите на вкладку **Chat** и задайте вопрос по тексту файла.
