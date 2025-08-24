from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm

User = get_user_model()

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Send verification email
        verification_url = self.request.build_absolute_uri(
            reverse_lazy('verify-email', kwargs={'token': self.object.email_verification_token})
        )
        send_mail(
            'Verify your email address',
            f'Please click the following link to verify your email: {verification_url} \n -QuizMaster App',
            settings.DEFAULT_FROM_EMAIL,
            [self.object.email],
            fail_silently=False,
        )        
        messages.success(self.request, 'Account created! Please check your email to verify your account.')
        return response

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        # Check if email is verified
        user = form.get_user()
        if not user.is_email_verified:
            # Resend verification email if not verified
            verification_url = self.request.build_absolute_uri(
                reverse_lazy('verify-email', kwargs={'token': user.email_verification_token})
            )
            send_mail(
                'Verify your email address',
                f'Please click the following link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.error(self.request, 'Please verify your email before logging in. A new verification email was sent')
            return self.form_invalid(form)
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('welcome-page')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        if user.user_type == 'admin':
            # For admin users, show all users
            users_list = User.objects.all() # CustomUser
            return render(request, 'users/admin_profile.html', {
                'user': user,
                'users_list': users_list
            })
        else:
            # For regular users, show only their profile
            return render(request, 'users/user_profile.html', {
                'user': user
            })

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
        else:
            messages.info(request, 'Your email is already verified.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link!')
    return redirect('login')