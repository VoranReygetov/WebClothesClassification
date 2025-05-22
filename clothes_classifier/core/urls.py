from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Головна сторінка
    path('detect/', views.detect, name='detect'),  # Обробка зображення
]