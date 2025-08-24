from django.shortcuts import render

def welcome_page(request):
    return render(request, 'welcome-page.html')


