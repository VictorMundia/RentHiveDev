"""
URL configuration for renthive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin  # Import Django admin module
from django.urls import path, include  # Import path and include functions for URL routing
from . import views  # Import views from the current directory
from users.views import custom_login

urlpatterns = [
    path('', views.home, name='home'),  # Route the root URL to the home view
    path('admin/', admin.site.urls),  # Route 'admin/' to the Django admin interface
    path('accounts/login/', custom_login, name='login'),  # Override default login with custom login
    path('accounts/', include('django.contrib.auth.urls')),  # Include built-in authentication URLs
    path('properties/', include('properties.urls')),  # Include URLs from the properties app
    path('maintenance/', include('maintenance.urls')),  # Include URLs from the maintenance app
    path('payments/', include('payments.urls')),  # Include URLs from the payments app
    path('users/', include('users.urls')),  # Include URLs from the users app
]
