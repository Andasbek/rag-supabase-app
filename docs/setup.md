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

    **Б. Функция поиска (`sql/01_match_chunks.sql`)**
    Этот скрипт создает RPC-функцию `match_chunks`, которая будет использоваться для поиска похожих векторов.

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
    ```

---

## Шаг 3: Установка Зависимостей

Рекомендуется использовать виртуальное окружение.

```bash
# Создание виртуального окружения (опционально)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Установка библиотек
pip install -r requirements.txt
```

---

## Шаг 4: Запуск Приложения

Вам потребуется запустить два процесса в двух разных терминалах.

### Терминал 1: Backend (FastAPI)
Запускает API сервер, который обрабатывает загрузку файлов и логику чата.

```bash
uvicorn backend.main:app --reload
```
*   API будет доступно по адресу: `http://localhost:8000`
*   Документация Swagger UI: `http://localhost:8000/docs`

### Терминал 2: Frontend (Streamlit)
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
