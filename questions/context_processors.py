from django.core.cache import cache
from .services import get_popular_tags_data, get_best_users_data

def sidebar(request):
    popular_tags = cache.get("popular_tags")

    if popular_tags is None:
        popular_tags = get_popular_tags_data()
        cache.set("popular_tags", popular_tags, timeout=60*60)

    best_users = cache.get("best_users")

    if best_users is None:
        best_users = get_best_users_data()
        cache.set("best_users", best_users, timeout=60*60)

    return {
        'popular_tags': popular_tags,
        'best_users': best_users,
    }