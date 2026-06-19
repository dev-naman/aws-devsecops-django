from django.test import TestCase
from django.db import IntegrityError
from app.models import UserMaster, AssetTracker

class UserMasterModelTests(TestCase):
    def test_create_user(self):
        """Test creating a standard user."""
        user = UserMaster.objects.create_user(
            username='model_user',
            email='model_user@example.com',
            password='password123',
            first_name='Model'
        )
        self.assertEqual(user.username, 'model_user')
        self.assertEqual(user.email, 'model_user@example.com')
        self.assertEqual(user.first_name, 'Model')
        self.assertTrue(user.check_password('password123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = UserMaster.objects.create_superuser(
            username='model_admin',
            email='model_admin@example.com',
            password='password123'
        )
        self.assertEqual(superuser.username, 'model_admin')
        self.assertEqual(superuser.email, 'model_admin@example.com')
        self.assertTrue(superuser.check_password('password123'))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_username_uniqueness(self):
        """Test that username must be unique."""
        UserMaster.objects.create_user(
            username='unique_user',
            email='user1@example.com',
            password='password123'
        )
        with self.assertRaises(IntegrityError):
            UserMaster.objects.create_user(
                username='unique_user',
                email='user2@example.com',
                password='password123'
            )

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        UserMaster.objects.create_user(
            username='user1',
            email='unique_email@example.com',
            password='password123'
        )
        with self.assertRaises(IntegrityError):
            UserMaster.objects.create_user(
                username='user2',
                email='unique_email@example.com',
                password='password123'
            )


class AssetTrackerModelTests(TestCase):
    def setUp(self):
        self.user = UserMaster.objects.create_user(
            username='asset_owner',
            email='owner@example.com',
            password='password123'
        )

    def test_create_asset_tracker(self):
        """Test creating an AssetTracker instance."""
        asset = AssetTracker.objects.create(
            user=self.user,
            asset_name='Test Laptop',
            asset_type='Hardware',
            issue_description='Keyboard is broken'
        )
        self.assertEqual(asset.user, self.user)
        self.assertEqual(asset.asset_name, 'Test Laptop')
        self.assertEqual(asset.asset_type, 'Hardware')
        self.assertEqual(asset.issue_description, 'Keyboard is broken')
        self.assertFalse(asset.ticket_closed)
        self.assertIsNotNone(asset.created_at)
        self.assertIsNotNone(asset.updated_at)

    def test_asset_tracker_str_representation(self):
        """Test the string representation of AssetTracker."""
        asset = AssetTracker.objects.create(
            user=self.user,
            asset_name='Test Desktop',
            asset_type='Hardware',
            issue_description='No display'
        )
        self.assertEqual(str(asset), 'Test Desktop')

    def test_cascade_deletion_on_user(self):
        """Test that deleting a user deletes their associated assets."""
        AssetTracker.objects.create(
            user=self.user,
            asset_name='Monitor',
            asset_type='Hardware',
            issue_description='Flickering screen'
        )
        self.assertEqual(AssetTracker.objects.count(), 1)
        self.user.delete()
        self.assertEqual(AssetTracker.objects.count(), 0)
