"""views functions for the :module:`windriver` django app"""
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from windriver import forms

@require_POST
def search_login(request):
    """logs vivisimo search crawler into a
    django regular user account account"""

    form = forms.SearchEngineAuthenticationForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password, method='ldap')
        login(request, user)

    return HttpResponse('Welcome, Crawler')
        

