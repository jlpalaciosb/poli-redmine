from django.contrib.auth.models import User
from django.test import TestCase

from .settings import LOGIN_URL, LOGIN_REDIRECT_URL


class BasicTestSetup(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='admin123')

    def login(self):
        self.client.login(username='user', password='admin123')


class LoginViewTest(BasicTestSetup):

    def test_login_template(self):

        response = self.client.get(LOGIN_URL)

        self.assertTemplateUsed(response, 'login/login.html')

    def test_login_success(self):
        self.credentials = {
            'username': 'user',
            'password': 'admin123'
        }
        self.client.post(LOGIN_URL, self.credentials, follow=True)

        self.assertIn('_auth_user_id', self.client.session)

    def test_login_success_redirect_index(self):
        self.credentials = {
            'username': 'user',
            'password': 'admin123'
        }
        response = self.client.post(LOGIN_URL, self.credentials, follow=True)

        self.assertRedirects(response, LOGIN_REDIRECT_URL)

    def test_login_error(self):
        self.credentials = {
            'username': 'user',
            'password': 'password_incorrecto'
        }
        response = self.client.post(LOGIN_URL, self.credentials, follow=True)

        self.assertNotIn('_auth_user_id', self.client.session)

        self.assertTrue(True if response.context['form'].errors else False)


class LogoutTest(BasicTestSetup):

    def test_logout(self):
        self.client.login(username='user', password='admin123')

        self.client.get('/logout/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_redirect(self):
        self.client.login(username='user', password='admin123')

        response = self.client.get('/logout/')

        self.assertRedirects(response, LOGIN_URL)
