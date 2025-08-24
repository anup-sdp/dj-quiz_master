from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Q
from .models import Quiz, Question, Option, QuizAttempt, UserAnswer, Category, Rating
from .forms import QuizForm, QuestionForm, OptionForm, TakeQuizForm, RatingForm, QuestionWithOptionsForm
from django.db import models


class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz/quiz_list.html'
    context_object_name = 'quizzes'
    
    def get_queryset(self):
        queryset = Quiz.objects.filter(is_active=True)
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        sort_by = self.request.GET.get('sort')
        if sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('ratings__score')).order_by('-avg_rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['sort_by'] = self.request.GET.get('sort', 'newest')
        return context

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quiz/quiz_detail.html'
    context_object_name = 'quiz'
    
    def get_queryset(self):
        return Quiz.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user_rating = Rating.objects.filter(quiz=self.object, user=self.request.user).first()
            context['user_rating'] = user_rating.score if user_rating else None
            context['rating_form'] = RatingForm(initial={'score': user_rating.score} if user_rating else None)
        return context

class QuizCreateView(LoginRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quiz/quiz_form.html'
    success_url = reverse_lazy('quiz-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Quiz created successfully!')
        return super().form_valid(form)

class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quiz/quiz_form.html'
    success_url = reverse_lazy('quiz-list')
    
    def test_func(self):
        quiz = self.get_object()
        return self.request.user == quiz.created_by or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Quiz updated successfully!')
        return super().form_valid(form)

class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = 'quiz/quiz_confirm_delete.html'
    success_url = reverse_lazy('quiz-list')
    
    def test_func(self):
        quiz = self.get_object()
        return self.request.user == quiz.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Quiz deleted successfully!')
        return super().delete(request, *args, **kwargs)

class TakeQuizView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quiz/take_quiz.html'
    context_object_name = 'quiz'
    
    def get_queryset(self):
        return Quiz.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TakeQuizForm(quiz=self.object)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TakeQuizForm(request.POST, quiz=self.object)
        
        if form.is_valid():
            start_time = timezone.now()
            with transaction.atomic():
                # Create quiz attempt
                attempt = QuizAttempt.objects.create(
                    user=request.user,
                    quiz=self.object,
                    max_score=self.object.questions.aggregate(total=models.Sum('points'))['total'] or 0
                )
                
                score = 0
                
                # Process each question
                for question in self.object.questions.all():
                    field_name = f"question_{question.id}"
                    selected_option_id = form.cleaned_data[field_name]
                    selected_option = Option.objects.get(id=selected_option_id)
                    
                    is_correct = selected_option.is_correct
                    if is_correct:
                        score += question.points
                    
                    # Save user answer
                    UserAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_option=selected_option,
                        is_correct=is_correct
                    )
                
                # Update attempt score and time taken
                attempt.score = score
                attempt.time_taken = timezone.now() - start_time
                attempt.save()
                
                # Send email with quiz results
                send_mail(
                    'Quiz Result',
                    f'Your result for {self.object.title}:\nScore: {score}/{attempt.max_score}\nTime taken: {attempt.time_taken}',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )
                
                messages.success(request, f'Quiz completed! Your score: {score}/{attempt.max_score}')
                return redirect('quiz-result', pk=attempt.pk)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

class QuizResultView(LoginRequiredMixin, DetailView):
    model = QuizAttempt
    template_name = 'quiz/quiz_result.html'
    context_object_name = 'attempt'
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

class MyQuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'quiz/my_quiz_list.html'
    context_object_name = 'quizzes'
    
    def get_queryset(self):
        return Quiz.objects.filter(created_by=self.request.user)

class UserQuizHistoryView(LoginRequiredMixin, ListView):
    model = QuizAttempt
    template_name = 'quiz/user_quiz_history.html'
    context_object_name = 'attempts'
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

class LeaderboardView(ListView):
    model = QuizAttempt
    template_name = 'quiz/leaderboard.html'
    context_object_name = 'leaderboard'
    
    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        if quiz_id:
            return QuizAttempt.objects.filter(quiz_id=quiz_id).order_by('-score', 'time_taken')
        return QuizAttempt.objects.values('user__username').annotate(
            total_score=models.Sum('score'),
            total_attempts=models.Count('id')
        ).order_by('-total_score')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.get('quiz_id')
        if quiz_id:
            context['quiz'] = get_object_or_404(Quiz, id=quiz_id)
        return context

class RateQuizView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RatingForm
    template_name = 'quiz/rate_quiz.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.quiz_id = self.kwargs['quiz_id']
        
        # Check if user already rated this quiz
        existing_rating = Rating.objects.filter(
            user=self.request.user,
            quiz_id=self.kwargs['quiz_id']
        ).first()
        
        if existing_rating:
            existing_rating.score = form.cleaned_data['score']
            existing_rating.save()
            messages.success(self.request, 'Your rating has been updated!')
        else:
            super().form_valid(form)
            messages.success(self.request, 'Thank you for rating!')
        
        return redirect('quiz-detail', pk=self.kwargs['quiz_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = get_object_or_404(Quiz, id=self.kwargs['quiz_id'])
        return context
    

class AddQuestionView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'quiz/add_question.html'
    
    def test_func(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_pk'])
        return self.request.user == quiz.created_by or self.request.user.is_staff
    
    def get(self, request, quiz_pk):
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        form = QuestionWithOptionsForm()
        return render(request, self.template_name, {'quiz': quiz, 'form': form})
    
    def post(self, request, quiz_pk):
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        form = QuestionWithOptionsForm(request.POST)
        
        if form.is_valid():
            with transaction.atomic():
                # Get the next order number
                next_order = quiz.questions.count() + 1
                
                # Create the question
                question = Question.objects.create(
                    quiz=quiz,
                    text=form.cleaned_data['question_text'],
                    order=next_order,  # Set order automatically
                    points=form.cleaned_data['points']
                )
                # Create the options
                correct_option = int(form.cleaned_data['correct_option'])
                for i in range(1, 5):
                    option_text = form.cleaned_data[f'option_{i}']
                    is_correct = (i == correct_option)
                    Option.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=is_correct
                    )
                
                messages.success(request, 'Question added successfully!')
                return redirect('quiz-detail', pk=quiz.pk)
        
        return render(request, self.template_name, {'quiz': quiz, 'form': form})