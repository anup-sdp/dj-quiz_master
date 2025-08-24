from django import forms
from .models import Quiz, Question, Option, Category, Rating

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'is_active', 'time_limit', 'max_questions', 'min_questions']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'order', 'points']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']

class TakeQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        super().__init__(*args, **kwargs)
        
        for question in quiz.questions.all():
            field_name = f"question_{question.id}"
            choices = [(option.id, option.text) for option in question.options.all()]
            self.fields[field_name] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 7})
        }