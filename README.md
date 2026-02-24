# GameForge (Django + PyMySQL) — No-code Game Editor + Runtime (Arcade)

## Что внутри
- **Editor (web)**: Django страницы + JS UI (дерево сцены, canvas, свойства, дерево файлов), авторизация/регистрация в модалке.
- **Runtime (python-пакет)**: загрузчик DSL, event bus, world/scene, системы и игровой цикл на `arcade`.
- **Shared**: Pydantic-схемы формата проекта.

## Быстрый запуск (dev)
1) Создай venv и установи зависимости:
   - `pip install -r requirements.txt`
2) Запусти миграции Django (нужны только для sessions/админки; проектные данные в MySQL через PyMySQL):
   - `python manage.py migrate`
3) Проверь доступ к MySQL базе `gameforge` (как в `core/db.py`).
4) Запуск:
   - `python manage.py runserver`

## Storage
Проекты пользователей дополнительно могут храниться в файловом storage:
`storage/user_projects/<email>/<project_name>/`

Путь задаётся в `gameforge_web/settings.py` как `USER_PROJECTS_ROOT`.

## Важно
- Django ORM для таблиц `gf_*` не используется намеренно: доступ идёт через `PyMySQL` в `core/db.py`.
- Для продакшна добавь нормальный хостинг статики, секреты через env, CSRF и т.п.
