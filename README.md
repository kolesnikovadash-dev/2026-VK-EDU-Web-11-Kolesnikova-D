# VK Education Web — HW 3

## Проект

Домашнее задание №3 по курсу VK Education Web.

Тема: **Вопросы и ответы**.

Реализована read-only версия сайта на Django:

- список новых вопросов;
- список популярных вопросов;
- список вопросов по тегу;
- страница одного вопроса со списком ответов;
- модели для пользователей, профилей, вопросов, ответов, тегов и лайков;
- management command для заполнения базы тестовыми данными;
- подключение PostgreSQL.

---

## Технологии

- Python
- Django
- PostgreSQL
- Bootstrap

---

## Структура проекта

```text
.
├── application/          # настройки Django-проекта
├── core/                 # общие view и утилиты
├── questions/            # модели, manager, management command
├── static/               # статические файлы
├── templates/            # HTML-шаблоны
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <ссылка-на-репозиторий>
cd <название-папки-проекта>
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
```

Активировать окружение:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать базу данных PostgreSQL

Например, через `psql`:

```sql
CREATE DATABASE "AskKolesnikova";
```

### 5. Настроить переменные окружения

Создать файл `.env` по примеру `.env.example`:

```env
POSTGRES_DB=AskKolesnikova
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Файл `.env` не добавляется в GitHub.

### 6. Применить миграции

```bash
python manage.py migrate
```

### 7. Заполнить базу тестовыми данными

Команда принимает коэффициент заполнения `ratio`:

```bash
python manage.py fill_db 10000
```

После выполнения команды будет создано:

```text
пользователей — ratio
вопросов — ratio * 10
ответов — ratio * 100
тэгов — ratio
оценок пользователей — ratio * 200
```

Для быстрого локального теста можно использовать маленькое значение:

```bash
python manage.py fill_db 100
```

### 8. Запустить сервер

```bash
python manage.py runserver
```

Сайт будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

---

## Основные страницы

```text
/                 — список новых вопросов
/hot/             — список популярных вопросов
/tag/<tag_name>/  — список вопросов по тегу
/question/<id>/   — страница одного вопроса
```

---

## Примечание

В проекте используется PostgreSQL. Стандартная SQLite-база данных не используется.
