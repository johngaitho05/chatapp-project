from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from .models import Contact, Message, ChatRoom
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.utils.safestring import mark_safe
import json


def root(request):
    return redirect('homepage')


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
                other_user = User.objects.get(username=phone)
                if other_user == user:
                    return render(request, 'chat/home.html',
                                  {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes',
                                   'error': "You can't add your own number to contacts"})
                else:
                    try:
                        contact = Contact.objects.get(owner=other_user, saver=user)
                        if contact.saved_as != contact.owner.username:
                            return render(request, 'chat/home.html',
                                          {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes',
                                           'error': 'That number already exists in your contacts', })
                        else:
                            print("auto saved contact. Editing...")
                            contact.saved_as = name
                            contact.save()
                            contacts = get_contacts(request.user)
                            return render(request, 'chat/home.html',
                                          {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes'})

                    except Contact.DoesNotExist:
                        new_contact = Contact(saver=user, owner=other_user, saved_as=name)
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
    active_contact = get_active_contact(request.user, room_name)
    room = get_or_create(room_name)
    texts_list = get_texts(room)
    chat_list = get_recents(request.user)
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
    chat_list = get_recents(request.user)
    return render(request, 'chat/home.html', {'recents': chat_list})


def get_contacts(user):
    all_contacts = user.contacts.all()
    saved_contacts = [contact for contact in all_contacts if contact.saved_as != contact.owner.username]
    if len(saved_contacts) == 1:
        count = '1 contact'
    else:
        count = str(len(saved_contacts)) + ' contacts'
    return [get_chat_rooms(saved_contacts, user), count]


# returns a list of recent chats to display on the homepage
def get_recents(user):
    contacts = Contact.objects.filter(saver=user)
    if contacts.count() > 0:
        chat_list = []
        for contact in contacts:
            room = get_chat_room(contact, user)
            if room.last_message:
                chat_list.append((contact, room))
        return chat_list
    return


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
    contact_owner = contact.owner
    if contact_owner.id < user.id:
        room_name = str(contact_owner.id) + 'A' + str(user.id)
    else:
        room_name = str(user.id) + 'A' + str(contact_owner.id)
    room = get_or_create(room_name)
    return room


def get_or_create(room_name):
    try:
        room = ChatRoom.objects.get(name=room_name)
    except ChatRoom.DoesNotExist:
        room = ChatRoom.objects.create(name=room_name)
    return room


def get_active_contact_username(user_id, chat_room):
    active_contact_id = get_active_contact_id(user_id, chat_room)
    active_contact_username = get_object_or_404(User, id=active_contact_id).username
    return active_contact_username


def get_active_contact(user, room_name):
    return get_object_or_404(User, id=get_active_contact_id(user.id, room_name))


def get_active_contact_id(user_id, room_name):
    id_list = room_name.split('A')
    if int(id_list[0]) == user_id:
        return int(id_list[1])
    elif int(id_list[1]) == user_id:
        return int(id_list[0])
    return -1


def get_texts(room):
    messages = Message.objects.filter(chat_room=room)
    date_list = [message.timestamp.date() for message in messages]
    date_set = sorted(set(date_list))
    texts_list = [None] * len(date_set)
    for i in range(len(date_set)):
        message_date = date_set[i]
        texts = [message for message in messages if
                 message.timestamp.date() == message_date]
        texts_list[i] = (message_date, texts)
    return texts_list


def update_receiver_contacts(user, room_name):
    receiver = get_active_contact(user, room_name)
    try:
        Contact.objects.get(saver=receiver, owner=user)
    except Contact.DoesNotExist:
        Contact.objects.create(saver=receiver, owner=user, saved_as=user.username)


def update_last_message(chat_room):
    message = Message.objects.filter(chat_room=chat_room).order_by('-timestamp').first()
    chat_room.last_message = message
    chat_room.save()
