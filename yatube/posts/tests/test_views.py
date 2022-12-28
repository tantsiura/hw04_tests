from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Category_1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='NoName2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем клиент автора тестового поста
        self.author_client = Client()
        self.author_client.force_login(PostsViewsTests.post.author)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'Category_1'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{PostsViewsTests.user.username}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostsViewsTests.post.pk}'}
            ),
            'posts/create_post.html': (
                reverse('posts:post_create')
            )
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
    
    
    def test_post_edit_by_author_uses_correct_template(self):
        """
        Проверка шаблона редактирования поста автором posts/create_post.html
        """
        response = self.author_client.\
            get(reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostsViewsTests.post.pk}'}
            )
            )
        self.assertTemplateUsed(response, 'posts/create_post.html')


class PostsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
    
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='NoName4')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        
        
    def test_index_show_correct_context(self):
        '''Шаблон index сформирован с правильным контекстом в части типов полей форм.'''
        response = self.authorized_client.get(reverse('posts:index'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea           
            'pub_date': forms.fields.DateTimeField,
            'group': forms.fields.SlugField,
            'author': forms.fields.CharField,
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)


    # Проверяем, что словарь context страницы /index
    # в первом элементе списка page_obj содержит ожидаемые значения 
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group
        
        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_group_0, self.post.group)

    # Проверяем, что словарь context страницы /group/test_group
    # содержит ожидаемые значения 
    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
            get(reverse('posts:group_list', kwargs={'slug': 'test_group'})))
        self.assertEqual(response.context.get('group').title, 'Тестовая группа')
        self.assertEqual(response.context.get('group').slug, 'test_group') 
        self.assertEqual(response.context.get('group').description, 'Тестовое описание группы')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName5')
        posts_list = []

        for i in range(0, 18):
            new_post = Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
            )
            posts_list.append(new_post)
        cls.post = Post.objects.bulk_create(posts_list)
    
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='NoName6')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 15. 
        self.assertEqual(len(response.context['page_obj']), 15)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3) 


class GroupContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName7')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
    
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='NoName8')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
    
    def test_post_with_group_on_the_correct_pages(self):
        '''Пост, созданный с указанием группы,
        отображается на соответствующих страницах:
        /index;
        /group/test_group/;
        /posts/profile/<username>.
        '''
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

        response = self.authorized_client.get(reverse('posts:group_list, {GroupContextTests.group.slug}'))
        self.assertEqual(first_object, self.post)

        response = self.authorized_client.get(reverse('posts:profile'))
        self.assertEqual(first_object, self.post)
