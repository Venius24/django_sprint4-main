from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth import get_user_model

from .forms import PostForm, CommentForm
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
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    template_name = 'blog/create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_username = self.kwargs['username']
        profile_object = get_object_or_404(User, username=target_username)
        context['profile'] = profile_object
        return context

    def get_queryset(self):
        # 1. Получаем имя пользователя из URL
        target_username = self.kwargs['username']
        
        # 2. Находим посты, где author__username совпадает с target_username
        queryset = Post.objects.filter(
            author__username=target_username
        ).order_by('-pub_date')
        
        return queryset


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.username})


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category_list'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.filter(
            is_published=True,
        ).order_by('-posts__pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug, is_published=True)
        context['category'] = category
        context['post_list'] = category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
        return context


class CommentCreateView(LoginRequiredMixin,CreateView):
    model = Comment
    form_class = CommentForm

    template_name = 'blog/comment.html'
    success_url = '/'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))

        form.instance.post = post
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk}) 


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