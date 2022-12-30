from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов
        '/auth/signup/', '/auth/login/', '/auth/logout/'.
        """
        response_author = self.guest_client.get('/auth/signup/')
        self.assertEqual(response_author.status_code, 200)
        response_tech = self.guest_client.get('/auth/login/')
        self.assertEqual(response_tech.status_code, 200)
        response_tech = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response_tech.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка доступности адресов
        '/auth/signup/', '/auth/login/', '/auth/logout/'.
        """
        response_author = self.guest_client.get('/auth/signup/')
        self.assertTemplateUsed(response_author, 'users/signup.html')
        response_tech = self.guest_client.get('/auth/login/')
        self.assertTemplateUsed(response_tech, 'users/login.html')
        response_tech = self.authorized_client.get('/auth/logout/')
        self.assertTemplateUsed(response_tech, 'users/logged_out.html')
