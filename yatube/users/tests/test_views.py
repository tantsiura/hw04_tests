from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName1')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names_for_guest = {
            'users/login.html': reverse('users:login'),
            'users/signup.html': reverse('users:signup'),

        }
        templ_pages_for_authorized_clnt = {
            'users/logged_out.html': reverse('users:logout')
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names_for_guest.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        for template, reverse_name in templ_pages_for_authorized_clnt.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
