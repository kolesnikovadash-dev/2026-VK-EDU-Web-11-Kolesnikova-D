from django.shortcuts import render, redirect, get_object_or_404
from .models import Question, Answer, Tag
from .utils import paginate
from django.contrib.auth.decorators import login_required
from .forms import AskForm, AnswerForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import QuestionLike, AnswerLike

def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, 20)
    return render(request, 'core/index.html', {'questions': page.object_list, 'page': page})

def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, 20)
    return render(request, 'core/hot.html', {'questions': page.object_list, 'page': page})

def question(request, question_id):
    question = get_object_or_404(
        Question.objects.with_stats(),
        pk=question_id
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/login/?continue={request.path}')

        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(
                question=question,
                author=request.user
            )

            answers = Answer.objects.filter(
                question=question
            ).select_related('author', 'author__profile').order_by('-rating', '-created_at')

            answer_ids = list(answers.values_list('id', flat=True))
            answer_index = answer_ids.index(answer.id)
            page_number = answer_index // 30 + 1

            return redirect(
                f'/question/{question.id}/?page={page_number}#answer-{answer.id}'
            )
    else:
        form = AnswerForm()

    answers = Answer.objects.filter(
        question=question
    ).select_related('author', 'author__profile').order_by('-rating', '-created_at')

    page = paginate(answers, request, 30)

    return render(request, 'core/question.html', {
        'question': question,
        'answers': page.object_list,
        'page': page,
        'form': form,
    })

@login_required(login_url='/login/', redirect_field_name='continue')
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect('question', question_id=question.id)
    else:
        form = AskForm()
    return render(request, 'core/ask.html', {
        'form': form
    })

def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_obj.name)
    page = paginate(questions, request, 20)
    return render(request, 'core/tag.html', {
        'questions': page.object_list,
        'page': page,
        'tag': tag_obj.name,
    })


@login_required(login_url='/login/', redirect_field_name='continue')
@require_POST
def vote_question(request):
    question_id = request.POST.get('id')
    try:
        value = int(request.POST.get('value'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'bad value'}, status=400)

    if value not in (1, -1):
        return JsonResponse({'error': 'bad value'}, status=400)

    question = get_object_or_404(Question, pk=question_id)
    like, created = QuestionLike.objects.get_or_create(
        question=question,
        user=request.user,
        defaults={'value': value}
    )

    if not created:
        if like.value == value:
            like.delete()
            question.rating -= value
        else:
            question.rating -= like.value
            question.rating += value
            like.value = value
            like.save()
    else:
        question.rating += value

    question.save(update_fields=['rating'])
    return JsonResponse({'rating': question.rating})


@login_required(login_url='/login/', redirect_field_name='continue')
@require_POST
def vote_answer(request):
    answer_id = request.POST.get('id')
    try:
        value = int(request.POST.get('value'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'bad value'}, status=400)

    if value not in (1, -1):
        return JsonResponse({'error': 'bad value'}, status=400)

    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        answer=answer,
        user=request.user,
        defaults={'value': value}
    )

    if not created:
        if like.value == value:
            like.delete()
            answer.rating -= value
        else:
            answer.rating -= like.value
            answer.rating += value
            like.value = value
            like.save()
    else:
        answer.rating += value

    answer.save(update_fields=['rating'])
    return JsonResponse({'rating': answer.rating})

@login_required(login_url='/login/', redirect_field_name='continue')
@require_POST
def mark_correct(request):
    question_id = request.POST.get('question_id')
    answer_id = request.POST.get('answer_id')

    answer = get_object_or_404(
        Answer.objects.select_related('question', 'question__author'),
        pk=answer_id,
        question_id=question_id
    )

    if answer.question.author != request.user:
        return JsonResponse({'error': 'forbidden'}, status=403)

    Answer.objects.filter(question=answer.question).update(is_correct=False)
    answer.is_correct = True
    answer.save(update_fields=['is_correct'])

    return JsonResponse({
        'answer_id': answer.id,
        'question_id': answer.question_id,
    })