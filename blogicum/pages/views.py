from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

def not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def server_error(request):
    return render(request, 'pages/500.html', status=500)

def permission_denied(request, exception):
    return render(request, 'pages/403csrf.html', status=403)

def csrf_failure(request, reason=""):
    return render(request, 'pages/403csrf.html', status=403)

class HomePageView(TemplateView):
    template_name = 'pages/about.html'

class Rules(TemplateView):
    template_name = 'pages/rules.html'