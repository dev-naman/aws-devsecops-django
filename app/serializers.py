from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import UserMaster,AssetTracker
from django.contrib.auth.hashers import make_password
class UserSerializer(ModelSerializer):
    class Meta:
        model = UserMaster
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
        '''
        By default Django will use this create method to create new object (instance)
        I have overrided the create method to hash the password and after hasing saving the password
        '''

class AssetTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTracker
        fields = ['id', 'user', 'asset_name', 'asset_type', 'issue_description', 'ticket_closed']
