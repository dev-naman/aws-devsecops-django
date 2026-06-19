from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import UserMaster

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = '/register'
        self.login_url = '/login'
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'first_name': 'Test'
        }

    def test_user_registration_success(self):
        """Test registering a new user successfully."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "user testuser created Successfully")

        # Verify user is in DB and password is secure/hashed
        user = UserMaster.objects.get(username='testuser')
        self.assertTrue(user.check_password('testpassword123'))

    def test_user_registration_invalid_data(self):
        """Test registration fails with invalid email."""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'not-an-email'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_list_excludes_password(self):
        """Test GET /register list of users does not expose passwords."""
        # Create a user first
        UserMaster.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        for user in response.data:
            self.assertNotIn('password', user)

    def test_user_login_success(self):
        """Test successful login returns JWT tokens."""
        # Create user
        UserMaster.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login fails with incorrect password."""
        UserMaster.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Invalid Credentials")

    def test_user_login_missing_fields(self):
        """Test login fails gracefully when username or password is missing."""
        login_data = {
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Username and password Required")
