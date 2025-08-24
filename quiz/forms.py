from django import forms
from .models import Quiz, Question, Option, Category, Rating

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-cyan-500 mb-1"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():            
            
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"  # ---
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': self.default_classes, 
                    'rows': 3,
                    'placeholder': f"Enter {field.label.lower()}",
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'type': 'date',
                    'placeholder': 'YYYY-MM-DD'
                })
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'type': 'time',
                    'placeholder': 'HH:MM'
                })    
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):                
                field.widget.attrs.update({
                    'class': "space-y-2"
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    'class': "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
                })
            else:              
                field.widget.attrs.update({
                    'class': self.default_classes
                })


class QuizForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'time_limit']

        
class QuestionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),           
        }		

class OptionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']


class TakeQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        
        choices = [(option.id, option.text) for option in self.question.options.all()]
        self.fields['answer'] = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect,
            required=True
        )

class RatingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 7})
        }
        
class QuestionWithOptionsForm(forms.Form):
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        label="Question"
    )
        
    # We'll create 4 option fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 5):
            self.fields[f'option_{i}'] = forms.CharField(
                label=f"Option {i}",
                widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
            )
        
        # Field to select the correct option
        self.fields['correct_option'] = forms.ChoiceField(
            choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
            widget=forms.RadioSelect,
            label="Correct Option"
        )

