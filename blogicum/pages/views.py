from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def about(request):
    template_name = 'pages/about.html'
    title = "О проекте"
    context = {
        'title': title
    }
    return render(request, template_name, context)

def rules(request):
    template_name = 'pages/rules.html'
    title = 'Наши правила'
    context = {
        'title': title,
    }
    return render(request, template_name, context)

def product_list(request):
    template_name = 'catalog/product_list.html'
    title = 'Список товаров ACME'
    products = [
      'Iron carrot',
      'Giant mousetrap',  
      'Dehydrated boulders',
      'Invisible paint',
    ]
    context = {
        'title': title,
        'products': products,
    }
    return render(request, template_name, context)