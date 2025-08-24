from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt, UserAnswer, Category, Rating

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    min_num = 2
    max_num = 10

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    inlines = [OptionInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'created_at', 'is_active', 'time_limit', 'question_count', 'average_rating')
    list_filter = ('is_active', 'created_at', 'category')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'
    
    def average_rating(self, obj):
        return f"{obj.average_rating:.1f}/7"
    average_rating.short_description = 'Avg Rating'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text', 'order', 'points')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [OptionInline]

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'max_score', 'completed_at', 'time_taken')
    list_filter = ('quiz', 'completed_at')
    search_fields = ('user__username', 'quiz__title')

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct')
    list_filter = ('is_correct', 'attempt__quiz')
    search_fields = ('attempt__user__username', 'question__text')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('quiz__title', 'user__username')