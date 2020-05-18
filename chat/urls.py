from django.urls import path
from . import views

urlpatterns = [
    path('', views.root),
    path('chat/contacts', views.show_contacts, name='show_contacts'),
    path('chat/add', views.add_contact, name='add_contact'),
    path('chat/<str:room_name>/', views.chat, name='chat'),
    path('chat/', views.home, name='homepage'),
]
