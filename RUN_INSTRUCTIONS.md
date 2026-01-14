# Запуск Проекта

Для удобства в проекте есть `Makefile`.

## Быстрый запуск

Одной командой запустить и Backend, и Frontend:
```bash
make run
```
*   API: `http://localhost:8000`
*   UI: `http://localhost:8501`
*   *Чтобы остановить, нажмите Ctrl+C*

## Другие команды

*   **Установка зависимостей**:
    ```bash
    make install
    ```

*   **Настройка окружения (venv)**:
    ```bash
    make venv
    ```

*   **Запуск только Backend**:
    ```bash
    make run-api
    ```

*   **Запуск только Frontend**:
    ```bash
    make run-ui
    ```

*   **Очистка временных файлов**:
    ```bash
    make clean
    ```

---

*Примечание*: Перед запуском убедитесь, что вы настроили `.env` (см. `docs/setup.md`).
