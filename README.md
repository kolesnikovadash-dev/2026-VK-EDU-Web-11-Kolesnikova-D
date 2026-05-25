# Домашнее задание 6 — Настройка веб-серверов

Проект: **Вопросы и Ответы**  
Стек: **Django + Gunicorn + nginx + PostgreSQL**

## Что было сделано

### 1. Настройка Gunicorn для Django

Создан конфигурационный файл `gunicorn.conf.py`.

Основные параметры:

```python
workers = 2
bind = "127.0.0.1:8000"

accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
```

Запуск Django-приложения через Gunicorn:

```bash
python -m gunicorn application.wsgi:application -c gunicorn.conf.py
```

Приложение доступно на:

```text
http://127.0.0.1:8000/
```

---

### 2. Создание простого WSGI-скрипта

Создан отдельный WSGI-скрипт `simple_wsgi.py`, который работает без Django.

Скрипт:

- запускается через Gunicorn;
- принимает GET-параметры;
- принимает POST-параметры;
- выводит их в ответе;
- работает на `localhost:8081`.

Запуск:

```bash
python -m gunicorn simple_wsgi:application --bind 127.0.0.1:8081
```

Проверка GET:

```bash
curl "http://127.0.0.1:8081/?a=10&b=hello"
```

Проверка GET + POST:

```bash
curl -X POST "http://127.0.0.1:8081/?a=10&b=hello" -d "x=123&y=test"
```

Пример ответа:

```text
GET params:
{'a': ['10'], 'b': ['hello']}

POST params:
{'x': ['123'], 'y': ['test']}
```

---

### 3. Настройка nginx для отдачи статического контента

nginx настроен для отдачи:

- `/uploads/` из директории `uploads`;
- `/media/` из директории `media`;
- `/static/` из директории `staticfiles`;
- файлов с расширениями `.css`, `.js`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.ico`, `.svg`, `.html`.

Для Django была добавлена настройка:

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

После этого выполнена команда:

```bash
python manage.py collectstatic
```

Результат:

```text
142 static files copied to staticfiles
```

Проверка отдачи static:

```bash
curl http://127.0.0.1/sample.html
```

Результат:

```text
hello static
```

Проверка отдачи uploads:

```bash
curl http://127.0.0.1/uploads/upload-test.txt
```

Результат:

```text
hello uploads
```

Также была настроена отдача файлов debug toolbar через `collectstatic`.

---

### 4. Настройка проксирования nginx → Gunicorn

В nginx настроен `upstream`:

```nginx
upstream django {
    server 127.0.0.1:8000;
}
```

Нестатические запросы проксируются на Gunicorn:

```nginx
location / {
    proxy_pass http://django;
    proxy_cache ask_cache;
    proxy_cache_valid 200 1m;
    add_header X-Proxy-Cache $upstream_cache_status;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

Приложение доступно через nginx:

```text
http://127.0.0.1/
```

---

### 5. Настройка proxy_cache

В nginx добавлена зона кэширования:

```nginx
proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone=ask_cache:10m max_size=100m inactive=10m use_temp_path=off;
```

Проверка кэша:

```bash
curl -I http://127.0.0.1/
curl -I http://127.0.0.1/
```

При повторном запросе nginx возвращает:

```text
X-Proxy-Cache: HIT
```

---

## Нагрузочное тестирование

Тестирование выполнялось с помощью ApacheBench:

```bash
ab -n 1000 -c 10 URL
```

Для динамических страниц использовался флаг `-l`, чтобы ApacheBench не считал ошибкой переменную длину ответа:

```bash
ab -l -n 1000 -c 10 URL
```

### Результаты

| № | Тест | Размер документа | Failed requests | Requests/sec | Time/request |
|---:|---|---:|---:|---:|---:|
| 1 | Static напрямую через nginx | 29000 bytes | 0 | 18600.50 | 0.538 ms |
| 2 | Static напрямую через Gunicorn | 22000 bytes | 0 | 5739.41 | 1.742 ms |
| 3 | Dynamic напрямую через Gunicorn | 58 bytes | 0 | 5485.37 | 1.823 ms |
| 4 | Dynamic через nginx proxy без cache | Variable | 0 | 4.16 | 2405.999 ms |
| 5 | Dynamic через nginx proxy_cache | Variable | 0 | 10049.14 | 0.995 ms |

---

## Выводы

### Насколько быстрее отдаётся статика через nginx по сравнению с WSGI/Gunicorn?

```text
nginx static:      18600.50 requests/sec
gunicorn static:    5739.41 requests/sec
```

```text
18600.50 / 5739.41 ≈ 3.24
```

**Статический документ через nginx отдаётся примерно в 3.2 раза быстрее**, чем через Gunicorn.

### Во сколько раз ускоряет работу proxy_cache?

```text
nginx proxy без cache:      4.16 requests/sec
nginx proxy_cache:      10049.14 requests/sec
```

```text
10049.14 / 4.16 ≈ 2415.66
```

**proxy_cache ускорил отдачу динамической страницы примерно в 2416 раз.**

Такой большой прирост связан с тем, что без кэша Django заново обрабатывает запрос, обращается к базе данных и рендерит страницу, а с кэшем nginx отдаёт уже готовый сохранённый ответ.

---

## Файлы результата

В проекте должны быть сохранены:

```text
gunicorn.conf.py
nginx.conf
simple_wsgi.py
static_wsgi.py
results_nginx_static.txt
results_gunicorn_static.txt
results_gunicorn_dynamic.txt
results_nginx_proxy.txt
results_nginx_proxy_cache.txt
```

---

## Использованные команды

### Gunicorn для Django

```bash
python -m gunicorn application.wsgi:application -c gunicorn.conf.py
```

### WSGI-скрипт без Django

```bash
python -m gunicorn simple_wsgi:application --bind 127.0.0.1:8081
```

### nginx

```bash
sudo nginx -t
sudo service nginx restart
```

### collectstatic

```bash
python manage.py collectstatic --noinput
```

### ApacheBench

```bash
ab -n 1000 -c 10 http://127.0.0.1/sample.html
ab -n 1000 -c 10 http://127.0.0.1:8082/
ab -n 1000 -c 10 "http://127.0.0.1:8081/?a=10&b=hello"
ab -l -n 1000 -c 10 http://127.0.0.1/
```
