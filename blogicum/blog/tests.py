from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Comment, Post
from .serializers import CommentSerializer


class BlogFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.author = user_model.objects.create_user(username='author')
        self.other = user_model.objects.create_user(username='other')
        self.category = Category.objects.create(
            title='News', description='News', slug='news'
        )
        self.post = Post.objects.create(
            title='First', text='Text', pub_date=timezone.now(),
            author=self.author, category=self.category,
        )

    def test_comment_creation_and_serializer(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('blog:add_comment', args=[self.post.pk]),
            {'text': 'Hello'},
        )
        self.assertRedirects(
            response, reverse('blog:post_detail', args=[self.post.pk])
        )
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(CommentSerializer(comment).data['text'], 'Hello')

    def test_other_user_cannot_delete_post(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('blog:delete_post', args=[self.post.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_missing_comment_returns_404(self):
        self.client.force_login(self.author)
        response = self.client.get(
            reverse('blog:edit_comment', args=[self.post.pk, 99999])
        )
        self.assertEqual(response.status_code, 404)

    def test_hidden_category_post_is_absent_from_other_profile(self):
        self.category.is_published = False
        self.category.save()
        self.client.force_login(self.other)
        response = self.client.get(
            reverse('blog:profile', args=[self.author.username])
        )
        self.assertNotContains(response, self.post.title)

    def test_hidden_category_post_rejects_new_comment(self):
        self.category.is_published = False
        self.category.save()
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('blog:add_comment', args=[self.post.pk]),
            {'text': 'Should not appear'},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Comment.objects.filter(post=self.post).exists())

    def test_anonymous_edit_and_delete_redirect_to_login(self):
        comment = Comment.objects.create(
            post=self.post, author=self.author, text='Existing'
        )
        urls = (
            reverse('blog:edit_post', args=[self.post.pk]),
            reverse('blog:delete_post', args=[self.post.pk]),
            reverse('blog:edit_comment', args=[self.post.pk, comment.pk]),
            reverse('blog:delete_comment', args=[self.post.pk, comment.pk]),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn('login', response.url)
