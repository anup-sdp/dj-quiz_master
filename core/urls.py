from django.urls import path
from .views import welcome_page


urlpatterns = [
	path('', welcome_page, name='welcome-page'),  # http://127.0.0.1:8000/
	
]