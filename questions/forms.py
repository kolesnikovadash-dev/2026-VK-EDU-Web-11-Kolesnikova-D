from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Question, Tag, Answer

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Ник',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_repeat = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(
        label='Аватарка',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Такой пользователь уже существует')
        return username
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password and password_repeat and password != password_repeat:
            self.add_error('password_repeat', 'Пароли не совпадают')

        return cleaned_data

class ProfileForm(forms.Form):
    username = forms.CharField(
        label='Ник',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(
        label='Аватарка',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_username(self):
        username = self.cleaned_data['username']

        users = User.objects.filter(username=username)

        if self.user is not None:
            users = users.exclude(pk=self.user.pk)

        if users.exists():
            raise ValidationError('Такой пользователь уже существует')

        return username

class AskForm(forms.Form):
    title = forms.CharField(
        label='Заголовок',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    text = forms.CharField(
        label='Текст вопроса',
        max_length=5000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6
        })
    )

    tags = forms.CharField(
        label='Теги',
        help_text='Введите до 3 тегов через запятую',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'python, django, forms'
        })
    )

    def clean_tags(self):
        raw_tags = self.cleaned_data['tags']

        tags = []

        for tag in raw_tags.split(','):
            tag = tag.strip().lower()

            if tag and tag not in tags:
                tags.append(tag)

        if not tags:
            raise forms.ValidationError('Добавьте хотя бы один тег')

        if len(tags) > 3:
            raise forms.ValidationError('Можно указать не больше 3 тегов')

        for tag in tags:
            if len(tag) > 50:
                raise forms.ValidationError('Длина тега не должна превышать 50 символов')

        return tags

    def save(self, author):
        question = Question.objects.create(
            title=self.cleaned_data['title'],
            text=self.cleaned_data['text'],
            author=author
        )

        tag_objects = []

        for tag_name in self.cleaned_data['tags']:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag)

        question.tags.set(tag_objects)

        return question

class AnswerForm(forms.Form):
    text = forms.CharField(
        label='Ваш ответ',
        max_length=5000,
        error_messages={
            'required': 'Введите текст ответа',
            'max_length': 'Ответ слишком длинный',
        },
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите ответ'
        })
    )

    def save(self, question, author):
        return Answer.objects.create(
            question=question,
            author=author,
            text=self.cleaned_data['text'],
        )