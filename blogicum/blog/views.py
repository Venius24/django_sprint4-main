from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Category, Location

def index(request):
    template_name = 'blog/index.html'
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    return render(request, template_name, {'post_list': post_list})

def post_detail(request, id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, id=id, is_published=True, category__is_published=True, pub_date__lte=timezone.now())
    context = {
        "post": post,
    }
    return render(request, template_name, context)

def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category_slug = get_object_or_404(Category, slug=category_slug, is_published=True)
    post_list = category_slug.posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()).order_by('-pub_date')
    context = {
        "category": category_slug,
        "post_list": post_list,
    }
    return render(request, template_name, context)


#        {{ post.pub_date|date:"d E Y" }} | {% if post.location and post.location.is_published %}{{ post.location.name }}{% else %}Планета Земля{% endif %}<br>
#        От автора @{{ post.author.username }} в категории {% include "includes/category_link.html" %}
#      </small>
#    </h6>
#    <p class="card-text">{{ post.text|truncatewords:10 }}</p>
#    <a href="{% url 'blog:post_detail' post.id %}" class="card-link">Читать полный текст</a>