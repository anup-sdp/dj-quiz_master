from django.urls import path
from . import views


urlpatterns = [
	path('', views.welcome_page, name='welcome-page'),  # http://127.0.0.1:8000/
	
]