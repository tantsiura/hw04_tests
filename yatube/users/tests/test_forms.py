from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.guest_client = Client()

    def test_signup_user_created(self):
        """ Проверка на добавление нового пользователя
        в базе данных при отправке формы /signup.
        """
        user_counts_before_test = User.objects.count()
        self.guest_client.post(
            reverse('users:signup'),
            data={
                'username': 'tester_test',
                'password1': 'Test_Moscow2022',
                'password2': 'Test_Moscow2022'
            }
        )
        self.assertGreater(User.objects.count(), user_counts_before_test)
