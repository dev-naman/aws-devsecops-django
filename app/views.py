from django.shortcuts import render
from .models import UserMaster,AssetTracker
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import APIView
from .serializers import UserSerializer,AssetTrackerSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from .utils import is_owner_or_superuser
class Register(APIView):
    # permission_classes = [IsAuthenticated,IsAdminUser] #Only Admin Users are allowed to perform this Action
    def get(self,request):
        print(request.user)
        users = UserMaster.objects.all()
        serializer = UserSerializer(users,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message":f"user {user.username} created Successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class Login(APIView):
    def post(self,request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'message':"Username and password Required"},status=400)
        user = UserMaster.objects.filter(username=request.data['username']).first()
        if user and user.check_password(request.data['password']): # check password is to check whether hashed password and user entered password is correct or not
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            return Response({'access_token':str(access_token),'refresh_token':str(refresh_token)})
            # res = Response()
            # res.data = {'message':"Login Success",}
            # res.status_code = 200
            # res.set_cookie('access_token',str(access_token))
            # res.set_cookie('refresh_token',str(refresh_token))
            # return res
        return Response({'message':"Invalid Credentials"},status=400)
    
class AssetTrackerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AssetTrackerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        asset_trackers = AssetTracker.objects.all()
        serializer = AssetTrackerSerializer(asset_trackers, many=True)
        return Response(serializer.data)

class AssetTrackerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieves an AssetTracker instance by its primary key.
        """
        try:
            # print(request.user)
            asset_tracker = AssetTracker.objects.get(pk=pk)
            serializer = AssetTrackerSerializer(asset_tracker)
            return Response(serializer.data)
        except AssetTracker.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        """
        Updates an AssetTracker instance partially.
        Only the owner or a superuser can make changes.
        """
        try:
            asset_tracker = AssetTracker.objects.get(pk=pk)
            if request.user == asset_tracker.user or request.user.is_superuser:
                serializer = AssetTrackerSerializer(asset_tracker, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("You are not authorized to update the item", status=400)
        except AssetTracker.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Deletes an AssetTracker instance.
        Only the owner or a superuser can delete.
        """
        try:
            asset_tracker = AssetTracker.objects.get(pk=pk)
            if is_owner_or_superuser(request, asset_tracker):
                asset_tracker.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response("You are not authorized to delete the item", status=400)
        except AssetTracker.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



