from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),  # Головна сторінка
    path('detect-image/', views.detect, name='detect_image'),
    path('detect-video/', views.detect_video, name='detect_video'),
    path('live-stream/', views.stream_video, name='stream_video'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)