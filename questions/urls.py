from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('tag/<slug:tag_name>/', views.tag, name='tag'),
    path('vote/question/', views.vote_question, name='vote_question'),
    path('vote/answer/', views.vote_answer, name='vote_answer'),
    path('mark-correct/', views.mark_correct, name='mark_correct'),
]