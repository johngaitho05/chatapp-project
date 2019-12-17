from django.urls import path
from . import views

urlpatterns = [
     path('contacts', views.show_contacts, name='show_contacts'),
     path('add',views.add_contact, name='add_contact'),
     path('<str:room_name>/', views.chat, name='chat'),
     path('', views.home, name='homepage'),
]