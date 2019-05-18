"""chatapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.root, name='root'),
    path('/<str:user_id>', views.home, name='homepage'),
    path('accounts/', include('accounts.urls')),
    path('contacts/', views.show_contacts, name='show_contacts'),
    path('contacts/add/',views.add_contact, name='add_contact'),
    path('chat/', views.start_chat, name='start_chat'),
    path('send_message/', views.send_message, name='send_message')
]
