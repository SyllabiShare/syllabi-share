from django.test import TestCase, Client
from django.contrib.auth.models import User
# Create your tests here.

class LoginTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='test', email='test@virginia.edu', password='top_secret')
        self.client1 = Client()
        self.client1.login(username='test', password='top_secret')

        self.user2 = User.objects.create_user(username='test1', email='test1@gmail.com', password='top_secret')
        self.client2 = Client()
        self.client2.login(username='test1', password='top_secret')

    def test_login_with_edu_email(self):
        response = str(self.client1.get('/').content)
        self.assertTrue('Wow!' in response)
        self.assertFalse('That was not a .edu email!' in response)

    def test_login_without_edu_email(self):
        response = str(self.client2.get('/').content)
        self.assertFalse('Welcome' in response)
        self.assertTrue('That was not a .edu email!' in response)
    
    def test_no_email(self):
        self.client1.logout()
        response = str(self.client1.get('/').content)
        self.assertFalse('Welcome' in response)
        self.assertFalse('That was not a .edu email!' in response)
