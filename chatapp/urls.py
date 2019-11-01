from django.urls import path,include
from contacts import views

urlpatterns = [
    path('', views.root, name='root'),
    path('<str:user_id>', views.home, name='homepage'),
    path('accounts/', include('accounts.urls')),
    path('admin/', include('admin.urls')),
    path('contacts/', views.show_contacts, name='show_contacts'),
    path('contacts/add/', views.add_contact, name='add_contact'),
    path('chat/', views.start_chat, name='start_chat'),
    path('send_message/', views.send_message, name='send_message')
]
