from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz-list'),
    path('my-quizzes/', views.MyQuizListView.as_view(), name='my-quiz-list'),
    path('quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz/new/', views.QuizCreateView.as_view(), name='quiz-create'),
    path('quiz/<int:pk>/edit/', views.QuizUpdateView.as_view(), name='quiz-update'),
    path('quiz/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz-delete'),
    path('quiz/<int:pk>/take/', views.TakeQuizView.as_view(), name='quiz-take'),
	path('quiz/<int:quiz_pk>/add-question/', views.AddQuestionView.as_view(), name='add-question'), 
    path('result/<int:pk>/', views.QuizResultView.as_view(), name='quiz-result'),
    path('history/', views.UserQuizHistoryView.as_view(), name='user-history'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/quiz/<int:quiz_id>/', views.LeaderboardView.as_view(), name='quiz-leaderboard'),
    path('rate/<int:quiz_id>/', views.RateQuizView.as_view(), name='rate-quiz'),
]