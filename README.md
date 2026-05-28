# Домашнее задание 7 — Дополнительные функции

Проект: **AskKolesnikova**  
Стек: **Django + PostgreSQL + Redis + Celery + Celery Beat + Centrifugo + Maildev + Bootstrap + JavaScript**

## Что реализовано

### 1. Redis + Celery + Celery Beat

В проект добавлены зависимости:

```text
celery
redis
django-redis
celery-redbeat
```

Redis используется:

- как брокер сообщений для Celery;
- как backend для результатов Celery;
- как backend кэша Django;
- как хранилище расписания Celery Beat через RedBeat.

В `settings.py` используются разные Redis DB:

```text
REDIS_CACHE_DB=0
REDIS_BROKER_DB=1
REDIS_BEAT_DB=2
```

Celery-приложение подключено через:

```text
application/celery.py
application/__init__.py
```

Проверка worker:

```bash
celery -A application inspect registered
```

Ожидаемые задачи:

```text
questions.tasks.update_popular_tags_cache
questions.tasks.update_best_users_cache
questions.tasks.send_new_answer_email_task
questions.tasks.publish_new_answer_task
```

---

### 2. Кэширование правой колонки

Реализовано кэширование блоков правой колонки:

- **Popular Tags** — 10 тегов с самым большим количеством вопросов за последние 3 месяца;
- **Best Members** — 10 пользователей по суммарному рейтингу вопросов и ответов за последнюю неделю.

Расчёт вынесен в:

```text
questions/services.py
```

Celery-задачи находятся в:

```text
questions/tasks.py
```

Задачи:

```text
update_popular_tags_cache
update_best_users_cache
```

Они пересчитывают данные и кладут их в Redis cache под ключами:

```text
popular_tags
best_users
```

В `questions/context_processors.py` данные берутся из кэша. Если кэша нет, выполняется fallback: данные считаются из БД и сразу сохраняются в Redis.

Периодический запуск настроен через `CELERY_BEAT_SCHEDULE` в `settings.py`.

---

### 3. Email-уведомления о новых ответах

При добавлении нового ответа автор вопроса получает email-уведомление.

Отправка письма выполняется не во view, а в отдельной Celery-задаче:

```text
send_new_answer_email_task
```

Для локальной разработки используется Maildev.

Maildev доступен по адресу:

```text
http://127.0.0.1:1080/
```

SMTP-порт:

```text
1025
```

---

### 4. Real-time сообщения через Centrifugo

Реализована отправка события о новом ответе в Centrifugo.

После добавления ответа запускается Celery-задача:

```text
publish_new_answer_task
```

Она публикует сообщение в канал:

```text
question:<question_id>
```

На странице вопроса подключён JavaScript-клиент Centrifugo:

```text
static/js/question_realtime.js
```

Поведение:

- если пользователь находится на первой странице ответов, новый ответ добавляется на страницу без перезагрузки;
- если пользователь находится не на первой странице, показывается alert о новом ответе.

Centrifugo admin доступен по адресу:

```text
http://127.0.0.1:8001/
```

Данные для локальной проверки:

```text
login: admin
password: admin
```

---

### 5. Полнотекстовый поиск

Реализован поиск по заголовку и тексту вопроса через PostgreSQL full-text search.

Backend endpoint:

```text
/search/suggest/?q=<query>
```

View:

```text
questions.views.search_suggest
```

Используются:

```python
SearchVector
SearchQuery
SearchRank
```

Frontend-подсказки реализованы в:

```text
static/js/search.js
```

Поведение:

- запрос отправляется автоматически при вводе текста;
- используется debounce 300 ms;
- подсказки отображаются выпадающим списком под поисковой строкой.

---

## Docker Compose

В `docker-compose.yml` добавлены сервисы:

```text
db
redis
web
celery
celerybeat
maildev
centrifugo
```

### Запуск через Docker Compose

Если Docker доступен без `sudo`:

```bash
docker compose up --build
```

Если Docker требует права:

```bash
sudo docker compose up --build
```

Основные адреса:

```text
Django:      http://127.0.0.1:8000/
Maildev:     http://127.0.0.1:1080/
Centrifugo:  http://127.0.0.1:8001/
PostgreSQL:  localhost:5432
Redis:       localhost:6379
```

---

## Локальный запуск без Docker

### 1. Активировать окружение

```bash
cd ~/projects/2026-VK-EDU-Web-11-Kolesnikova-D-hw-3
source .venv-linux/bin/activate
```

### 2. Запустить Redis

```bash
sudo service redis-server start
redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

### 3. Запустить Maildev

Можно запустить только Maildev через Docker:

```bash
sudo docker compose up maildev
```

Maildev будет доступен:

```text
http://127.0.0.1:1080/
```

### 4. Запустить Centrifugo

```bash
sudo docker compose up centrifugo
```

Админка:

```text
http://127.0.0.1:8001/
```

### 5. Запустить Celery worker

В отдельном терминале:

```bash
cd ~/projects/2026-VK-EDU-Web-11-Kolesnikova-D-hw-3
source .venv-linux/bin/activate
celery -A application worker -l info
```

### 6. Запустить Celery Beat

В отдельном терминале:

```bash
cd ~/projects/2026-VK-EDU-Web-11-Kolesnikova-D-hw-3
source .venv-linux/bin/activate
celery -A application beat -l info
```

### 7. Запустить Django

```bash
python manage.py runserver 0.0.0.0:8000
```

Открыть:

```text
http://127.0.0.1:8000/
```

---

## Проверка функциональности

### Проверка Django

```bash
python manage.py check
```

Ожидаемый результат:

```text
System check identified no issues
```

### Проверка Celery

```bash
celery -A application inspect registered
```

В списке должны быть задачи:

```text
questions.tasks.update_popular_tags_cache
questions.tasks.update_best_users_cache
questions.tasks.send_new_answer_email_task
questions.tasks.publish_new_answer_task
```

### Проверка кэша

```bash
python manage.py shell
```

```python
from django.core.cache import cache
cache.get("popular_tags")
cache.get("best_users")
```

### Проверка email

1. Открыть вопрос.
2. Добавить новый ответ.
3. Проверить логи Celery worker.
4. Открыть Maildev:

```text
http://127.0.0.1:1080/
```

### Проверка real-time

1. Открыть один и тот же вопрос в двух вкладках.
2. В первой вкладке добавить ответ.
3. Во второй вкладке новый ответ должен появиться без перезагрузки или должен появиться alert.

### Проверка поиска

Открыть endpoint напрямую:

```text
http://127.0.0.1:8000/search/suggest/?q=test
```

Или начать вводить текст в поисковую строку в шапке сайта.

---

## Основные изменённые файлы

```text
application/celery.py
application/settings.py
application/__init__.py
docker-compose.yml
centrifugo/config.json
questions/services.py
questions/tasks.py
questions/context_processors.py
questions/views.py
questions/urls.py
questions/templates/core/question.html
templates/base.html
static/js/search.js
static/js/question_realtime.js
requirements.txt
.env.example
```

---

## Примечания

Секретные значения в учебном проекте вынесены в переменные окружения и отражены в `.env.example`.

Файл `.env` не должен попадать в Git.
