from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count


class Tag(models.Model):
    name = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='тег',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ['name']

class QuestionManager(models.Manager):
    def with_stats(self):
        return self.select_related(
            'author'
        ).prefetch_related(
            'tags'
        ).annotate(
            answers_count=Count('answers', distinct=True),
        )

    def new(self):
        return self.with_stats().order_by('-created_at')

    def hot(self):
        return self.with_stats().order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self.with_stats().filter(tags__name=tag_name).order_by('-rating', '-created_at')

class Question(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='заголовок',
    )
    text = models.TextField(
        max_length=5000,
        verbose_name='текст вопроса',
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='автор',
    )
    tags = models.ManyToManyField(
        'questions.Tag',
        related_name='questions',
        verbose_name='теги',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    rating = models.IntegerField(
        default=0,
        verbose_name='рейтинг',
    )

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/question/{self.pk}/'

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'
        ordering = ['-created_at']

class Answer(models.Model):
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='вопрос',
    )
    text = models.TextField(
        max_length=5000,
        verbose_name='текст ответа',
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='автор',
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='правильный ответ',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    rating = models.IntegerField(
        default=0,
        verbose_name='рейтинг',
    )

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
        ordering = ['-rating', '-created_at']

class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTE_CHOICES = (
        (LIKE, 'лайк'),
        (DISLIKE, 'дизлайк'),
    )

    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='вопрос',
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='question_votes',
        verbose_name='пользователь',
    )
    value = models.SmallIntegerField(
        choices=VOTE_CHOICES,
        verbose_name='оценка',
    )

    def __str__(self):
        return f'{self.user} -> {self.question}: {self.value}'

    class Meta:
        verbose_name = 'оценка вопроса'
        verbose_name_plural = 'оценки вопросов'
        unique_together = ('question', 'user')

class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTE_CHOICES = (
        (LIKE, 'лайк'),
        (DISLIKE, 'дизлайк'),
    )

    answer = models.ForeignKey(
        'questions.Answer',
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='ответ',
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='answer_votes',
        verbose_name='пользователь',
    )
    value = models.SmallIntegerField(
        choices=VOTE_CHOICES,
        verbose_name='оценка',
    )

    def __str__(self):
        return f'{self.user} -> answer {self.answer_id}: {self.value}'

    class Meta:
        verbose_name = 'оценка ответа'
        verbose_name_plural = 'оценки ответов'
        unique_together = ('answer', 'user')