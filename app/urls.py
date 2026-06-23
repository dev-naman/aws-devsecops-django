from django.contrib import admin
from django.urls import path
from .import views
from .views import health
urlpatterns = [
    path("health/", health),
    path('register', views.Register.as_view()),
    path('login',views.Login.as_view()),
    path('asset',views.AssetTrackerView.as_view()),
    path('modify/asset/<int:pk>/',views.AssetTrackerDetailView.as_view()),
]
