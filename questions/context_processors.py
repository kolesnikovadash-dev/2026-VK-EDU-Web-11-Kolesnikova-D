from django.contrib.auth.models import User
from django.db.models import Count
from .models import Tag


def sidebar(request):
    popular_tags = Tag.objects.annotate(
        questions_count=Count('questions')
    ).order_by('-questions_count')[:20]

    best_users = User.objects.annotate(
        questions_count=Count('questions'),
        answers_count=Count('answers'),
    ).order_by('-questions_count', '-answers_count')[:10]

    return {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }