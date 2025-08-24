# users, forms.py:
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django import forms

# Mixin to apply style to form fields
class FormStyleMixin:  # was StyledFormMixin2
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-cyan-500 mb-1"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            # Get field label safely, fallback to field name if label is None, eg password in UserCreationForm
            field_label = field.label if field.label else field_name.replace('_', ' ')
            
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    #'placeholder': f"Enter {field.label.lower()}"  
                    'placeholder': field_label
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': field_label  # ---
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': field_label  # ---
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': self.default_classes, 
                    'rows': 3,
                    'placeholder': field_label,
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

class CustomUserCreationForm(FormStyleMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False)
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "phone_number")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        if user.is_superuser:
            user.user_type = 'admin'
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(FormStyleMixin, AuthenticationForm):
    username = forms.CharField(label="Username")


class UserUpdateForm(forms.ModelForm): # use FormStyleMixin,  ?
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "phone_number", "bio")
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})