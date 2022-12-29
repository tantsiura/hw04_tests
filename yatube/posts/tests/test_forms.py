from django.contrib.auth import get_user_model
from ..models import Group, Post
from posts.forms import PostForm
from posts.models import Post
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        # Создаем запись в базе данных для проверки сушествующего slug
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_for_test = Post.objects.create(
            author = self.user,
            text = 'Тестовый пост'
        )        

    def test_create_post(self):
        """Валидная форма создает пост."""
        # Подсчитаем количество записей в Posts
        posts_count_before_test = Post.objects.count()  
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={
                    'username': f'{PostFormTests.user.username}'
                    }))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count_before_test+1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                slug='testovyij-zagolovok',
                text='Тестовый текст'
            ).exists()
        )
