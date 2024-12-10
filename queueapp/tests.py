import httpx
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Line, Registration
from django.urls import reverse
from rest_framework import status

class APITestCase(TestCase):
    def setUp(self):
        self.client = httpx.Client(base_url='https://trackseries.sagarkundu.live')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.line = Line.objects.create(
            name='Test Line',
            pincode='123456',
            registration_start_time='2024-12-10T00:00:00Z',
            capacity=10,
            current_count=0,
            details='Test line details'
        )

    def test_signup(self):
        url = reverse('user-signup')
        data = {
            'username': 'newuser',
            'password': 'newpass',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.json())

    def test_login(self):
        url = reverse('user-login')
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.json())

    def test_logout(self):
        url = reverse('user-logout')
        headers = {'Authorization': f'Token {self.token.key}'}
        response = self.client.post(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_join_queue(self):
        url = reverse('line-join', kwargs={'pk': self.line.id})
        headers = {'Authorization': f'Token {self.token.key}'}
        data = {
            'name': 'Test User',
            'mobile': '1234567890',
            'aadhaar_no': '123456789012',
            'dob': '1990-01-01'
        }
        response = self.client.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_leave_queue(self):
        # First, join the queue
        Registration.objects.create(
            user=self.user,
            line=self.line,
            name='Test User',
            mobile='1234567890',
            aadhaar_no='123456789012',
            dob='1990-01-01',
            position=1
        )
        self.line.current_count = 1
        self.line.save()

        url = reverse('line-leave', kwargs={'pk': self.line.id})
        headers = {'Authorization': f'Token {self.token.key}'}
        response = self.client.post(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_queues(self):
        # Create a registration for the user
        Registration.objects.create(
            user=self.user,
            line=self.line,
            name='Test User',
            mobile='1234567890',
            aadhaar_no='123456789012',
            dob='1990-01-01',
            position=1
        )

        url = reverse('registration-my-queues')
        headers = {'Authorization': f'Token {self.token.key}'}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def tearDown(self):
        self.client.close()

