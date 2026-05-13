# VK Education Web — HW 5

## Проект

## Домашнее задание 5: загрузка картинок и AJAX

В рамках ДЗ-5 добавлена загрузка и отображение аватарок пользователей, а также обработка AJAX-запросов для голосования и отметки правильного ответа.

### Реализовано

- загрузка аватарки пользователя через форму регистрации и редактирования профиля;
- хранение изображений через `ImageField`;
- настройка `MEDIA_URL` и `MEDIA_ROOT`;
- отображение загруженных аватарок в шапке, карточках вопросов и ответах;
- AJAX-лайки и дизлайки вопросов;
- AJAX-лайки и дизлайки ответов;
- AJAX-отметка правильного ответа;
- проверка, что правильный ответ может выбрать только автор вопроса;
- проверка авторизации, CSRF и метода POST для AJAX-запросов.

### Основные URL

- `/profile/edit/` — редактирование профиля и аватарки;
- `/vote/question/` — AJAX-голосование за вопрос;
- `/vote/answer/` — AJAX-голосование за ответ;
- `/mark-correct/` — AJAX-отметка правильного ответа.

### Проверка проекта

```bash
python manage.py check
python manage.py runserver
```

## Технологии

- Python 3.12
- Django 6
- PostgreSQL
- Bootstrap
- Docker Compose
- Django Debug Toolbar
- Pillow

---

## Структура проекта

```text
.
├── application/          # настройки Django-проекта
├── core/                 # общие страницы, ошибки, модель профиля
├── questions/            # модели вопросов, ответов, тегов, оценок
├── static/               # статические файлы
├── templates/            # общие HTML-шаблоны
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Основной запуск через Docker Compose

### 1. Клонировать репозиторий

```bash
git clone <ссылка-на-репозиторий>
cd <название-папки-проекта>
```

### 2. Запустить контейнеры

```bash
docker compose up --build
```

Будут запущены:

- `web` — Django-приложение;
- `db` — PostgreSQL.

Сайт будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

---

## Миграции и заполнение базы через Docker

После запуска контейнеров выполнить миграции:

```bash
docker compose exec web python manage.py migrate
```

Создать суперпользователя для админки:

```bash
docker compose exec web python manage.py createsuperuser
```

Заполнить базу тестовыми данными:

```bash
docker compose exec web python manage.py fill_db 1000
```

Команда принимает коэффициент заполнения `ratio`.

После выполнения команды создаётся:

```text
пользователей — ratio
вопросов — ratio * 10
ответов — ratio * 100
тэгов — ratio
оценок пользователей — ratio * 200
```

Для быстрого локального теста можно использовать меньшее значение:

```bash
docker compose exec web python manage.py fill_db 100
```

---

## Локальный запуск без Docker

### 1. Создать виртуальное окружение

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

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Создать PostgreSQL-базу

Например, через `psql`:

```sql
CREATE DATABASE "AskKolesnikova";
```

### 4. Создать `.env`

Создать файл `.env` по примеру `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
POSTGRES_DB=AskKolesnikova
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Файл `.env` не добавляется в GitHub.

### 5. Применить миграции

```bash
python manage.py migrate
```

### 6. Создать суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Заполнить базу

```bash
python manage.py fill_db 1000
```

Для быстрой проверки можно использовать:

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
/admin/           — Django Admin
/__debug__/       — Django Debug Toolbar при DEBUG=True
```

---

## Модели

В проекте реализованы основные сущности:

- `Profile` — профиль пользователя;
- `Tag` — тег вопроса;
- `Question` — вопрос;
- `Answer` — ответ;
- `QuestionLike` — оценка вопроса;
- `AnswerLike` — оценка ответа.

Для моделей настроены:

- связи `ForeignKey`, `OneToOneField`, `ManyToManyField`;
- `verbose_name` и `verbose_name_plural`;
- метод `__str__`;
- сортировка через `class Meta`;
- ограничения `unique_together` для запрета повторного голосования;
- поддержка лайков и дизлайков через поле `value`;
- денормализованное поле `rating` для вопросов и ответов;
- `SlugField` для тегов;
- `ImageField` для аватарки профиля с сохранением по пути `avatars/год/месяц/день/`.

---

## Management command

Команда заполнения базы:

```bash
python manage.py fill_db [ratio]
```

Пример:

```bash
python manage.py fill_db 1000
```

Команда использует Django ORM и создаёт тестовые данные пакетно через `bulk_create`.

При повторном запуске команда создаёт новые тестовые данные с уникальными именами пользователей и тегов.

---

## Админка

Для основных моделей настроена Django Admin.

Админка доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```

Перед входом нужно создать суперпользователя:

```bash
python manage.py createsuperuser
```

или при запуске через Docker:

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Debug Toolbar

При `DEBUG=True` подключён Django Debug Toolbar.

Панель используется для проверки количества SQL-запросов и времени генерации страниц.

Адрес:

```text
http://127.0.0.1:8000/__debug__/
```

---

## Обработка ошибок

В проекте добавлены обработчики ошибок:

- `404` — страница не найдена;
- `500` — ошибка сервера.

Кастомные страницы ошибок используются при `DEBUG=False`.

---

## Примечание

В проекте используется PostgreSQL. Стандартная SQLite-база данных не используется.
