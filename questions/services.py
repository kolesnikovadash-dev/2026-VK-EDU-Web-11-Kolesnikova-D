from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q, Value, IntegerField, F
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Tag

def get_popular_tags_data():
    since = timezone.now() - timedelta(days=90)
    tags = Tag.objects.filter(
        questions__created_at__gte=since
    ).annotate(
        questions_count=Count("questions", distinct=True)
    ).order_by("-questions_count")[:10]
    data = []
    for tag in tags:
        data.append({
            "name": tag.name,
            "questions_count": tag.questions_count,
        })
    return data

def get_best_users_data():
    since = timezone.now() - timedelta(days=7)
    users = User.objects.annotate(
        questions_score=Coalesce(
            Sum("questions__rating", filter=Q(questions__created_at__gte=since)),
            Value(0),
            output_field=IntegerField()
        )
    ).annotate(
        answers_score=Coalesce(
            Sum("answers__rating", filter=Q(answers__created_at__gte=since)),
            Value(0),
            output_field=IntegerField()
        )
    ).annotate(
        total_score=F("questions_score") + F("answers_score")
    ).order_by("-total_score")[:10]
    data = []
    for user in users:
        data.append({
            "username": user.username,
            "score": user.total_score,
        })
    return data