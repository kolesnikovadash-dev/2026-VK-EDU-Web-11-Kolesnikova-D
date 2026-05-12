from django.shortcuts import render, get_object_or_404
from .models import Question, Answer, Tag
from .utils import paginate


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, 20)
    return render(request, 'core/index.html', {'questions': page.object_list, 'page': page})


def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, 20)
    return render(request, 'core/hot.html', {'questions': page.object_list, 'page': page})


def question(request, question_id):
    question = get_object_or_404(Question.objects.with_stats(), pk=question_id)
    answers = Answer.objects.filter(question=question).select_related('author').order_by('-rating', '-created_at')
    page = paginate(answers, request, 30)
    return render(request, 'core/question.html', {
        'question': question,
        'answers': page.object_list,
        'page': page,
    })


def ask(request):
    return render(request, 'core/ask.html')


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_obj.name)
    page = paginate(questions, request, 20)
    return render(request, 'core/tag.html', {
        'questions': page.object_list,
        'page': page,
        'tag': tag_obj.name,
    })