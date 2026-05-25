from django.contrib import admin
from .models import Tag, Question, Answer, QuestionLike, AnswerLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'rating', 'created_at')
    search_fields = ('title', 'text')
    list_filter = ('created_at', 'tags')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'rating', 'is_correct', 'created_at')
    search_fields = ('text',)
    list_filter = ('is_correct', 'created_at')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'value')
    list_filter = ('value',)


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'user', 'value')
    list_filter = ('value',)