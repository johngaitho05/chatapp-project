from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from .models import Contact, Message, ChatRoom
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import operator
from datetime import date, timedelta
from django.utils.safestring import mark_safe
import json


@login_required
def show_contacts(request):
    contacts = get_contacts(request.user)
    if not contacts[0]:
        return render(request, 'chat/home.html',
                      {'count': contacts[1], 'message': 'You have not added any contact'})
    else:
        return render(request, 'chat/home.html',
                      {'count': contacts[1], 'contacts': contacts[0]})


@login_required
def add_contact(request):
    contacts = get_contacts(request.user)
    if request.method == 'GET':
        try:
            phone_number = request.GET['phone_number']
        except MultiValueDictKeyError:
            phone_number = ''
        if not contacts[0]:
            if phone_number:
                return render(request, 'chat/home.html',
                              {'count': '0 chat', 'message':
                                  'You have not added any contact', 'add': 'yes', 'phone_number': phone_number})
            return render(request, 'chat/home.html',
                          {'count': '0 chat', 'message': 'You have not added any contact', 'add': 'yes'})
        if phone_number:
            return render(request, 'chat/home.html',
                          {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes', 'phone_number': phone_number})
        return render(request, 'chat/home.html',
                      {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes', })
    elif request.method == 'POST':
        user = request.user
        name = request.POST['name']
        phone = request.POST['phone']
        if name and phone:
            try:
                new_user = User.objects.get(username=phone)
                if new_user == user:
                    return render(request, 'chat/home.html',
                                  {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes',
                                   'error': "You can't add your own number to contacts"})
                else:
                    try:
                        contact = Contact.objects.get(phone=phone, user=user)
                        if contact.name != contact.phone:
                            return render(request, 'chat/home.html',
                                          {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes',
                                           'error': 'That number already exists in your contacts', })
                        else:
                            contact.name = name
                            contact.save()
                            contacts = get_contacts(request.user)
                            return render(request, 'chat/home.html',
                                          {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes'})

                    except Contact.DoesNotExist:
                        new_contact = Contact(user=user, phone=phone, name=name)
                        new_contact.save()
                        contacts = get_contacts(request.user)
                        return render(request, 'chat/home.html',
                                      {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes'})

            except User.DoesNotExist:
                return render(request, 'chat/home.html',
                              {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes',
                               'error': 'Number not registered with smartchat'})

        else:
            return render(request, 'chat/home.html',
                          {'count': contacts[1], 'contacts': contacts[0],
                           'add': 'yes', 'error': 'All fields are required'})


def delete_contact(request):
    pass


def update_contact(request):
    pass


@login_required
def chat(request, room_name):
    today = date.today()
    yesterday = today - timedelta(1)
    json_data = {'room_name': mark_safe(json.dumps(room_name)),
                 'username': mark_safe(json.dumps(request.user.username))}
    active_contact = get_object_or_404(Contact, user=request.user,
                                       phone=get_active_contact_username(request.user.id, room_name))
    texts_list = get_texts(room_name)
    chat_list = get_chat_list(request.user)
    if not texts_list:
        texts_list = 'Null'
    if chat_list is not None:
        return render(request, 'chat/home.html',
                      {'texts_list': texts_list,
                       'active_contact': active_contact,
                       'recents': chat_list[::-1],
                       'json_data': json_data,
                       'today': today,
                       'yesterday': yesterday})
    else:
        return render(request, 'chat/home.html',
                      {'texts_list': texts_list,
                       'active_contact': active_contact,
                       'recents': 'Null',
                       'json_data': json_data,
                       'today': today,
                       'yesterday': yesterday})


@login_required
def home(request):
    chat_list = get_chat_list(request.user)
    return render(request, 'chat/home.html', {'recents': chat_list})


def get_contacts(user):
    all_contacts = Contact.objects.filter(user=user)
    saved_contacts = [contact for contact in all_contacts if contact.name != contact.phone]
    if len(saved_contacts) == 1:
        count = '1 contact'
    else:
        count = str(len(saved_contacts)) + ' contacts'

    user_contacts = [contact for contact in saved_contacts]
    return [get_chat_rooms(user_contacts, user), count]


# returns a list of recent chats to display on the homepage
def get_chat_list(user):
    contacts = Contact.objects.filter(user=user)
    if contacts.count() > 0:
        chat_list = []
        for contact in contacts:
            room = get_chat_room(contact, user)
            if room.last_message:
                chat_list.append((contact, room, formatted_text(room.last_message.content)))
        return chat_list
    return


def formatted_text(text):
    if len(text) > 40:
        return text[:40] + '...'
    else:
        return text


def add_chat_rooms(current_user):
    all_users = User.objects.all()
    other_users = all_users.exclude(id=current_user.id)
    for user in other_users:
        new_room = str(user.id) + 'A' + str(current_user.id)
        ChatRoom.objects.create(name=new_room)


def get_chat_rooms(contacts, user):
    chat_rooms = [(contact, get_chat_room(contact, user)) for contact in contacts]
    return chat_rooms


def get_chat_room(contact, user):
    contact_owner = User.objects.get(username=contact.phone)
    if contact_owner.id < user.id:
        room_name = str(contact_owner.id) + 'A' + str(user.id)
    else:
        room_name = str(user.id) + 'A' + str(contact_owner.id)
    try:
        room = ChatRoom.objects.get(name=room_name)
    except ChatRoom.DoesNotExist:
        chatroom_messages = Message.objects.filter(chat_room=room_name).order_by('-timestamp')
        if chatroom_messages:
            messages_list = [message for message in chatroom_messages]
            room = ChatRoom.objects.create(name=room_name, last_message=messages_list[0])
        else:
            room = ChatRoom.objects.create(name=room_name)
    return room


def get_active_contact_username(user_id, chat_room):
    active_contact_id = get_active_contact_id(user_id, chat_room)
    active_contact_username = get_object_or_404(User, id=active_contact_id).username
    return active_contact_username


def get_active_contact_id(user_id, chat_room):
    id_list = chat_room.split('A')
    if int(id_list[0]) == user_id:
        return int(id_list[1])
    elif int(id_list[1]) == user_id:
        return int(id_list[0])
    else:
        get_object_or_404(User, id=-1)


def get_texts(room_name):
    messages = Message.objects.filter(chat_room=room_name)
    date_list = [message.timestamp.date() for message in messages]
    date_set = sorted(set(date_list))
    texts_list = [None] * len(date_set)
    for i in range(len(date_set)):
        message_date = date_set[i]
        texts = [(message, message.timestamp.time()) for message in messages if
                 message.timestamp.date() == message_date]
        texts_list[i] = (message_date, texts)
    return texts_list


def update_receiver_contacts(user, chat_room):
    phone = get_active_contact_username(user.id, chat_room)
    receiver = User.objects.get(username=phone)
    try:
        Contact.objects.get(user=receiver, phone=user.username)
    except Contact.DoesNotExist:
        Contact.objects.create(user=receiver, phone=user.username, name=user.username)


def update_last_message(room_name):
    try:
        chat_room = ChatRoom.objects.get(name=room_name)
        message = Message.objects.filter(chat_room=chat_room).order_by('-timestamp').first()
        chat_room.last_message = message
        chat_room.save()
    except ChatRoom.DoesNotExist:
        print('Chat room not found!')
