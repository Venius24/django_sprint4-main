from django.db import models
from django.conf import settings
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=256, verbose_name = 'Заголовок')
    text = models.TextField(verbose_name = 'Текст')
    pub_date = models.DateTimeField(verbose_name = 'Дата и время публикации',
                                    help_text='Если установить дату и время в будущем — можно делать отложенные публикации.',
                                    default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name = 'Автор публикации')
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True, verbose_name = 'Местоположение')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=False, verbose_name = 'Категория', related_name='posts')
    is_published = models.BooleanField(default=True, verbose_name = 'Опубликовано', help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = 'Добавлено')

    image = models.ImageField(
        'Фото', upload_to='birthday/', null=True, blank=True
    )

    class Meta:
        verbose_name = 'публикация' 
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return f'Номер поста {self.pk}'


class Category(models.Model):
    title = models.CharField(max_length=256, verbose_name = 'Заголовок')
    description = models.TextField(verbose_name = 'Описание')
    slug = models.SlugField(unique=True, verbose_name = 'Идентификатор', help_text='Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано', help_text='Снимите галочку, чтобы скрыть публикацию.')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Добавлено')

    class Meta:
        verbose_name = 'категория' 
        verbose_name_plural = 'Категории'
        
    def __str__(self):
        return self.title 


class Location(models.Model):
    name = models.CharField(max_length=256, verbose_name = 'Название места')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано', help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = 'Добавлено')

    class Meta:
        verbose_name = 'местоположение' 
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий {self.pk} к посту {self.post.pk}'
