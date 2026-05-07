from django.shortcuts import render
from .utils import paginate

def index(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'Question {i}',
            'text': f'Text {i}',
        })

    page = paginate(questions, request, 10)

    return render(request, 'core/index.html', {
        'questions': page.object_list,
        'page': page,
    })

def hot(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'Hot Question {i}',
            'text': f'Hot Text {i}',
        })

    page = paginate(questions, request, 10)

    return render(request, 'core/hot.html', {
        'questions': page.object_list,
        'page': page,
    })

def question(request, question_id):
    question = {
        'id': question_id,
        'title': f'Question {question_id}',
        'text': f'Text {question_id}',
    }

    answers = []
    for i in range(1, 5):
        answers.append(f'Answer {i}')

    return render(request, 'core/question.html', {
        'question': question,
        'answers': answers
    })

def ask(request):
    return render(request, 'core/ask.html')

def tag(request, tag_name):
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'{tag_name} Question {i}',
            'text': f'Text {i}',
        })

    page = paginate(questions, request, 10)
    return render(request, 'core/tag.html', {
        'questions': page.object_list,
        'page': page,
        'tag': tag_name,
    })