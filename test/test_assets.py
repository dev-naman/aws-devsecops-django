from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import UserMaster, AssetTracker
from rest_framework_simplejwt.tokens import AccessToken

class AssetTrackerTests(APITestCase):
    def setUp(self):
        # Create users
        self.owner = UserMaster.objects.create_user(
            username='owner_user',
            email='owner@example.com',
            password='password123'
        )
        self.other_user = UserMaster.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='password123'
        )
        self.superuser = UserMaster.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='password123'
        )

        # Create tokens
        self.owner_token = str(AccessToken.for_user(self.owner))
        self.other_token = str(AccessToken.for_user(self.other_user))
        self.superuser_token = str(AccessToken.for_user(self.superuser))

        # Create an asset owned by self.owner
        self.asset = AssetTracker.objects.create(
            user=self.owner,
            asset_name='MacBook Pro',
            asset_type='Laptop',
            issue_description='Battery draining too fast',
            ticket_closed=False
        )

        self.asset_url = '/asset'
        self.asset_detail_url = f'/modify/asset/{self.asset.id}/'

    def test_unauthenticated_requests_blocked(self):
        """Test that unauthenticated requests to asset endpoints are rejected."""
        # GET list
        response = self.client.get(self.asset_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # POST create
        response = self.client.post(self.asset_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # GET detail
        response = self.client.get(self.asset_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_asset_success(self):
        """Test that an authenticated user can create an asset tracker ticket."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        data = {
            'user': self.owner.id,
            'asset_name': 'iPhone 15',
            'asset_type': 'Mobile',
            'issue_description': 'Screen cracked',
            'ticket_closed': False
        }
        response = self.client.post(self.asset_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['asset_name'], 'iPhone 15')
        self.assertEqual(response.data['user'], self.owner.id)

    def test_get_all_assets(self):
        """Test getting all assets list."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        response = self.client.get(self.asset_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['asset_name'], 'MacBook Pro')

    def test_get_asset_detail(self):
        """Test getting details of a specific asset."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        response = self.client.get(self.asset_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_name'], 'MacBook Pro')

    def test_get_asset_detail_not_found(self):
        """Test retrieving non-existent asset returns 404."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        response = self.client.get('/modify/asset/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_patch_asset(self):
        """Test asset owner is authorized to update it."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        data = {'ticket_closed': True}
        response = self.client.patch(self.asset_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ticket_closed'])

    def test_non_owner_cannot_patch_asset(self):
        """Test another user cannot update someone else's asset."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token}')
        data = {'ticket_closed': True}
        response = self.client.patch(self.asset_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "You are not authorized to update the item")

    def test_superuser_can_patch_any_asset(self):
        """Test superuser can update any user's asset."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.superuser_token}')
        data = {'ticket_closed': True}
        response = self.client.patch(self.asset_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['ticket_closed'])

    def test_owner_can_delete_asset(self):
        """Test owner can delete their own asset."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.owner_token}')
        response = self.client.delete(self.asset_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AssetTracker.objects.filter(id=self.asset.id).exists())

    def test_non_owner_cannot_delete_asset(self):
        """Test another user cannot delete someone else's asset."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token}')
        response = self.client.delete(self.asset_detail_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "You are not authorized to delete the item")
        self.assertTrue(AssetTracker.objects.filter(id=self.asset.id).exists())

    def test_superuser_can_delete_any_asset(self):
        """Test superuser can delete any user's asset."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.superuser_token}')
        response = self.client.delete(self.asset_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AssetTracker.objects.filter(id=self.asset.id).exists())
