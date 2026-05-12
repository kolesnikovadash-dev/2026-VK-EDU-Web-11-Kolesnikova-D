import random
import time
from collections import defaultdict

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike


BATCH_SIZE = 1000


class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def make_votes(self, model, obj_field, objects, users, count):
        votes = []
        ratings = defaultdict(int)
        used = set()

        max_count = len(objects) * len(users)
        count = min(count, max_count)

        while len(votes) < count:
            obj = random.choice(objects)
            user = random.choice(users)
            pair = (obj.id, user.id)

            if pair in used:
                continue

            used.add(pair)
            value = random.choice([model.LIKE, model.DISLIKE])

            votes.append(model(
                **{obj_field: obj},
                user=user,
                value=value,
            ))

            ratings[obj.id] += value

        model.objects.bulk_create(votes, batch_size=BATCH_SIZE)
        return ratings

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']

        if ratio <= 0:
            self.stdout.write(self.style.ERROR('ratio must be positive'))
            return

        prefix = int(time.time())
        password = make_password('password')

        self.stdout.write(f'Filling database with ratio={ratio}...')

        users = User.objects.bulk_create([
            User(
                username=f'user_{prefix}_{i}',
                email=f'user_{prefix}_{i}@mail.com',
                password=password,
            )
            for i in range(ratio)
        ], batch_size=BATCH_SIZE)

        Profile.objects.bulk_create([
            Profile(user=user)
            for user in users
        ], batch_size=BATCH_SIZE)

        tags = Tag.objects.bulk_create([
            Tag(name=f'tag-{prefix}-{i}')
            for i in range(ratio)
        ], batch_size=BATCH_SIZE)

        questions = Question.objects.bulk_create([
            Question(
                title=f'Question {prefix}-{i}',
                text=f'Text of question {prefix}-{i}',
                author=random.choice(users),
            )
            for i in range(ratio * 10)
        ], batch_size=BATCH_SIZE)

        question_tag_model = Question.tags.through
        question_tag_model.objects.bulk_create([
            question_tag_model(question_id=question.id, tag_id=tag.id)
            for question in questions
            for tag in random.sample(tags, k=min(3, len(tags)))
        ], batch_size=BATCH_SIZE)

        answers = Answer.objects.bulk_create([
            Answer(
                question=random.choice(questions),
                text=f'Text of answer {prefix}-{i}',
                author=random.choice(users),
            )
            for i in range(ratio * 100)
        ], batch_size=BATCH_SIZE)

        question_ratings = self.make_votes(
            QuestionLike,
            'question',
            questions,
            users,
            ratio * 100,
        )

        answer_ratings = self.make_votes(
            AnswerLike,
            'answer',
            answers,
            users,
            ratio * 100,
        )

        for question in questions:
            question.rating = question_ratings.get(question.id, 0)

        for answer in answers:
            answer.rating = answer_ratings.get(answer.id, 0)

        Question.objects.bulk_update(questions, ['rating'], batch_size=BATCH_SIZE)
        Answer.objects.bulk_update(answers, ['rating'], batch_size=BATCH_SIZE)

        self.stdout.write(self.style.SUCCESS('Database filled successfully'))