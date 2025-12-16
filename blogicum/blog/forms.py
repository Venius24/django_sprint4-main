from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Post, Comment


User = get_user_model()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        include = ('image')
        exclude = ('author',)
        widgets = {
            # Важно: формат iso нужен для корректной работы datetime-local
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
