from django.shortcuts import render, redirect, get_object_or_404
from chat.models import Contact, Message, ChatRoom
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import operator
from datetime import date, datetime
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
        phone_number = request.GET['phone_number']
        if not contacts[0]:
            if phone_number:
                return render(request, 'chat/home.html',
                              {'count': '0 chat', 'message':
                                  'You have not added any contact', 'add': 'yes','phone_number':phone_number})
            return render(request, 'chat/home.html',
                          {'count': '0 chat', 'message': 'You have not added any contact', 'add': 'yes'})
        if phone_number:
            return render(request, 'chat/home.html',
                          {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes','phone_number':phone_number})
        return render(request, 'chat/home.html',
                  {'count': contacts[1], 'contacts': contacts[0], 'add': 'yes',})
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
    now = datetime.now()
    formatted_date = datetime.strftime(now, '%d-%m-%Y')
    room_to_json = mark_safe(json.dumps(room_name))
    username_json = mark_safe(json.dumps(request.user.username))
    active_contact = get_object_or_404(Contact, user=request.user,
                                       phone=get_active_contact_username(request.user.id, room_name))
    texts = Message.objects.filter(chat_room=room_name).order_by('timestamp')
    texts_list = get_texts(texts)
    chat_list = get_chat_list(request.user)
    if not texts_list:
        texts_list = 'Null'
    if chat_list is not None:
        return render(request, 'chat/home.html',
                      {'texts_list': texts_list,
                       'active_contact': active_contact,
                       'recents': chat_list[::-1],
                       'room_name_json': room_to_json,
                       'username_json': username_json,
                       'today': formatted_date})
    else:
        return render(request, 'chat/home.html',
                      {'texts_list': texts_list,
                       'active_contact': active_contact,
                       'recents': 'Null',
                       'room_name_json': room_to_json,
                       'username_json': username_json,
                       'today': formatted_date})


@login_required
def home(request):
    chat_list = get_chat_list(request.user)
    if chat_list is not None:
        return render(request, 'chat/home.html', {'recents': chat_list})
    else:
        return render(request, 'chat/home.html', {'recents': 'Null'})


def get_contacts(user):
    all_contacts = Contact.objects.filter(user=user)
    saved_contacts = []
    for contact in all_contacts:
        if contact.name != contact.phone:
            saved_contacts.append(contact)
    if len(saved_contacts) == 1:
        num = '1 contact'
    else:
        num = str(len(saved_contacts)) + ' contacts'

    user_contacts = [contact for contact in saved_contacts]
    return [get_chat_rooms(user_contacts, user), num]


# returns a list of recent chats to display on the homepage
def get_chat_list(user):
    contacts = Contact.objects.filter(user=user)
    contacts_list = [contact for contact in contacts]
    if len(contacts_list) > 0:
        chat_list = []
        for contact in contacts:
            room = get_chat_room(contact, user)
            if room.last_message != '':
                chat_list.append((contact, room, formatted_text(room.last_message)))
        if len(chat_list) == 0:
            return
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
    chat_rooms = []
    for contact in contacts:
        room = get_chat_room(contact, user)
        chat_rooms.append((contact, room))
    return chat_rooms


def get_chat_room(contact, user):
    contact_owner = User.objects.get(username=contact.phone)
    if contact_owner.id < user.id:
        room_name = str(contact_owner.id) + 'A' + str(user.id)
    else:
        room_name = str(user.id) + 'A' + str(contact_owner.id)
    room = get_object_or_404(ChatRoom, name=room_name)
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


def update_last_message(chat_room, message):
    current_room = ChatRoom.objects.get(name=str(chat_room))
    current_room.last_message = message
    current_room.save()


def get_texts(messages):
    date_list = []
    texts_list = []
    for message in messages:
        message_date = datetime.strftime(message.timestamp, "%d-%m-%Y")
        date_list.append(message_date)
    date_set = set(date_list)
    for message_date in date_set:
        texts = []
        for message in messages:
            if datetime.strftime(message.timestamp, "%d-%m-%Y") == message_date:
                texts.append((message, datetime.strftime(message.timestamp, "%H:%M")))
        texts_list.append((message_date, texts))
    return texts_list


def update_receiver_contacts(user, chat_room):
    phone = get_active_contact_username(user.id,chat_room)
    receiver = User.objects.get(username=phone)
    try:
        Contact.objects.get(user=receiver,phone=user.username)
    except Contact.DoesNotExist:
        Contact.objects.create(user=receiver,phone=user.username,name=user.username)


def get_current_time():
    pass
