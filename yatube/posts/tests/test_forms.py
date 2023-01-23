from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст'
        )
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст'}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.last().id, self.post.id)
        self.assertEqual(Post.objects.first().group, self.post.group)
        self.assertEqual(Post.objects.first().text, self.post.text)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        self.group = Group.objects.create( 
            title='Тестовая группа', 
            slug='test-slug', 
            description='Тестовое описание', 
        ) 
        self.post = Post.objects.create( 
            author=self.user, 
            text='Тестовый текст', 
            group=self.group, 
        ) 
        posts_count = Post.objects.count()
        form_data = {'text': 'Изменяем текст', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'], 
            group=form_data['group']
        ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_not_create_guest_client(self):
        """Валидная форма не изменит запись в Post если неавторизован."""
        self.group = Group.objects.create( 
            title='Тестовая группа', 
            slug='test-slug', 
            description='Тестовое описание', 
        ) 
        self.post = Post.objects.create( 
            author=self.user, 
            text='Тестовый текст', 
            group=self.group, 
        )
        posts_count = Post.objects.count()
        form_data = {'text': 'Изменяем текст', 'group': self.group.id}
        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(
            text=form_data['text'], 
            group=form_data['group']
        ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
