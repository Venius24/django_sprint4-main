from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, Location, Comment

User = get_user_model()

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        ).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    template_name = 'blog/create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.author.username})

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    template_name = 'blog/create.html'
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)  

    def form_valid(self, form):
        return super().form_valid(form)
    
    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.author.username}) 

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = '/'

    def get_success_url(self):
        return reverse('pages:index') 


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context
    
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.author.username}) 

    
class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        # Сохраняем пользователя в атрибут класса, чтобы не искать его дважды
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        queryset = Post.objects.filter(author=self.author)

        if self.request.user != self.author:
            queryset = queryset.filter(pub_date__lte=timezone.now(), is_published=True)

        return queryset.order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем уже найденного автора
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    # Используем поля, которые ожидает тест (имя, фамилия, почта)
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = '/'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        # Получаем пользователя из URL (username)
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        
        # Проверяем, что текущий пользователь редактирует свой профиль
        if user != self.request.user:
            raise PermissionDenied
        
        return user

    def form_valid(self, form):
        # Явно сохраняем форму (хотя UpdateView это делает)
        user = form.save()
        messages.success(self.request, 'Профиль успешно обновлён.')  # Опционально
        return super().form_valid(form)

    def form_invalid(self, form):
        # Temporary debug: save form errors to disk for diagnostics
        try:
            from pathlib import Path
            Path('profile_form_errors.txt').write_text(str(form.errors))
        except Exception:
            pass
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Возвращаем на страницу профиля
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category_list'
    paginate_by = 10

    def get_queryset(self):
        # 1. Сначала находим нужную категорию по slug
        self.category = get_object_or_404(
            Category, 
            slug=self.kwargs['category_slug'], 
            is_published=True
        )
        # 2. Возвращаем только те посты, которые относятся к этой категории
        # и проходят фильтрацию по публикации
        return self.category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        # Добавляем саму категорию в контекст, чтобы вывести её заголовок в шаблоне
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin,CreateView):
    model = Comment
    form_class = CommentForm

    template_name = 'blog/comment.html'
    success_url = '/'

    def form_valid(self, form):
        post = get_object_or_404(
            Post,  
            pk=self.kwargs.get('post_id'),
            is_published=True,
            pub_date__lte=timezone.now())

        form.instance.post = post
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()

        return super().form_valid(form)
    
    def get_success_url(self):
        # Редирект на профиль
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class CommentUpdateView(LoginRequiredMixin,UpdateView):
    model = Comment
    form_class = CommentForm

    template_name = 'blog/comment.html'
    success_url = '/'

    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        comment = instance.comments.get(pk=kwargs['comment_id'])
        if comment.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)  

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk}) 
    
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = '/'

    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        comment = instance.comments.get(pk=kwargs['comment_id'])
        if comment.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk}) 