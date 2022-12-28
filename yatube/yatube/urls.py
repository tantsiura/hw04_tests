from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace='index')),
    path('admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
]
