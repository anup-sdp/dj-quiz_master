from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Max

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='quizzes')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes", null=True, blank=True)
    max_questions = models.PositiveIntegerField(default=50)
    min_questions = models.PositiveIntegerField(default=5)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return sum(rating.score for rating in ratings) / len(ratings)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.text[:50]}..."
    
    def save(self, *args, **kwargs):
        # If this is a new question (no pk yet), set the order automatically
        if not self.pk:
            # Get the current maximum order number for this quiz
            max_order = Question.objects.filter(quiz=self.quiz).aggregate(Max('order'))['order__max']
            # If there are no questions yet, start with 1, otherwise increment by 1
            self.order = (max_order or 0) + 1
        
        super().save(*args, **kwargs)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.text[:30]}... - {self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}/{self.max_score}"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question.text[:30]}... - {self.selected_option.text}"

class Rating(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text="Rate this quiz from 1 to 7"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('quiz', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}/7"