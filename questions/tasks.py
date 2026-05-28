from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from .models import Tag
from django.contrib.auth.models import User

from django.db.models import Count, Sum, Q, Value, IntegerField, F
from django.db.models.functions import Coalesce

from .services import get_popular_tags_data, get_best_users_data

from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import Question, Answer

import requests
from django.conf import settings

@shared_task
def update_popular_tags_cache():
    data = get_popular_tags_data()
    cache.set("popular_tags", data, timeout=60*60)
    return data

@shared_task
def update_best_users_cache():
    data = get_best_users_data()
    cache.set("best_users", data, timeout=60*60)
    return data

@shared_task
def send_new_answer_email_task(question_id, answer_id):
    question = Question.objects.select_related("author").get(id=question_id)
    answer = Answer.objects.select_related("author").get(id=answer_id)

    recipient = question.author.email
    if not recipient:
        return "Question author has no email"

    question_url = reverse("question", kwargs={"question_id": question.id})

    subject = "New answer on your question"
    message = (
        f"На ваш вопрос появился новый ответ.\n\n"
        f"Вопрос: {question.title}\n"
        f"Автор ответа: {answer.author.username}\n\n"
        f"Ссылка: {question_url}"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )

    return f"Email sent to {recipient}"

@shared_task
def publish_new_answer_task(question_id, answer_id):
    answer = Answer.objects.select_related("author").get(id=answer_id)

    channel = f"question:{question_id}"

    data = {
        "question_id": question_id,
        "answer_id": answer.id,
        "text": answer.text,
        "author": answer.author.username,
        "rating": answer.rating,
        "is_correct": answer.is_correct,
        "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M"),
    }

    response = requests.post(
        settings.CENTRIFUGO_API_URL,
        headers={
            "Authorization": f"apikey {settings.CENTRIFUGO_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "method": "publish",
            "params": {
                "channel": channel,
                "data": data,
            },
        },
        timeout=3,
    )

    response.raise_for_status()
    return data