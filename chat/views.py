from django.shortcuts import render, redirect, get_object_or_404
from chat.models import Contact, Message,ChatRoom
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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
                          {'count': contacts[1], 'chatrooms': contacts[0]})


@login_required
def add_contact(request):
    if request.method == 'GET':
        contacts = get_contacts(request.user)
        if not contacts[0]:
            return render(request, 'chat/home.html',
                          {'count': '0 chat', 'message': 'You have not added any contact', 'add': 'yes'})
        return render(request, 'chat/home.html',
                      {'count': contacts[1], 'chatrooms': contacts[0], 'add': 'yes'})
    elif request.method == 'POST':
        user = request.user
        try:
            new_user= User.objects.get(username=request.POST['phone'])
            contacts = get_contacts(user)
            if new_user == user:
                return render(request, 'chat/home.html',
                              {'count': contacts[1], 'chatrooms': contacts[0], 'add': 'yes',
                               'error': 'You cant add your own number to contacts', })

            elif request.POST['phone'] != "" and request.POST['name'] != "":
                try:
                    Contact.objects.get(phone=request.POST['phone'], user=user)
                    return render(request, 'chat/home.html',
                                  {'count': contacts[1], 'chatrooms': contacts[0], 'add': 'yes',
                                   'error': 'That number already exists in your contacts', })
                except Contact.DoesNotExist:
                    new_contact = Contact(user=user, phone=request.POST['phone'], name=request.POST['name'],
                                          last_message="")
                    new_contact.save()
                    contacts=get_contacts(user)
                    return render(request, 'chat/home.html',
                                  {'count': contacts[1], 'chatrooms': contacts[0], 'add': 'yes'})
            else:
                contacts=get_contacts(user)
                return render(request, 'chat/home.html',
                              {'count': contacts[1], 'chatrooms': contacts[0],
                               'add': 'yes', 'error': 'All fields are required'})
        except User.DoesNotExist:
            contacts = get_contacts(user)
            if not contacts[0]:
                return render(request, 'chat/home.html',
                              {'count': '0 chat', 'message': 'You have not added any contact', 'add': 'yes',
                               'error': 'Number not registered with smartchat'})
            else:
                return render(request, 'chat/home.html',
                              {'count': contacts[1], 'chatrooms': contacts[0], 'add': 'yes',
                               'error': 'Number not registered with smartchat'})


def delete_contact(request):
    pass


def update_contact(request):
    pass


@login_required
def chat(request,room_name):
    today = date.today()
    formatted_date = date.strftime(today, '%d-%m-%Y')
    room_to_json = mark_safe(json.dumps(room_name))
    username_json = mark_safe(json.dumps(request.user.username))
    active_contact = get_object_or_404(Contact, user=request.user,
                                       phone=get_active_contact_username(request.user.id, room_name))
    texts = Message.objects.filter(chat_room=room_name).order_by('timestamp')
    texts_list = get_texts(texts)
    chat_list = get_chat_list(request.user)
    if not texts_list:
        texts_list = 'Null'
    if chat_list:
        return render(request, 'chat/home.html',
                      {'texts_list': texts_list,
                       'active_contact': active_contact,
                       'recents': chat_list[::-1],
                       'room_name_json':room_to_json,
                       'username_json':username_json,
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
        return render(request, 'chat/home.html', {'recents': chat_list[::-1]})
    else:
        return render(request, 'chat/home.html', {'recents': 'Null'})


def get_contacts(user):
    my_contacts = Contact.objects.filter(user=user)
    count = []
    for contact in my_contacts:
        count.append(contact)
    if len(count) == 1:
        num = '1 contact'
    else:
        num = str(len(count)) + ' chat'

    mylist = [contact for contact in my_contacts]
    return [get_chat_rooms(mylist, user), num]


# returns a list of recent chats to display on the homepage
def get_chat_list(user):
    contacts = Contact.objects.filter(user=user)
    recent_chats = contacts.exclude(last_message='')
    if recent_chats:
        chat_dict = {}
        for recent_chat in recent_chats:
            chat_dict.update({recent_chat: recent_chat.last_message})
        chat_list = []
        for contact, text in chat_dict.items():
            chat_list.append((contact, formatted_text(text), get_chat_room(contact, user)))

        return chat_list
    return None


def formatted_text(text):
    if len(text) > 40:
        return text[:40] + '...'
    else:
        return text


def add_chat_room(current_user):
    all_users = User.objects.all()
    other_users = all_users.exclude(id=current_user.id)
    rooms_list = []
    for user in other_users:
        new_room = str(user.id) + 'A' + str(current_user.id)
        rooms_list.append(new_room)
    ChatRoom.objects.create(slot=current_user.id,rooms=rooms_list)


def get_chat_rooms(contacts, user):
    chat_rooms = []
    for contact in contacts:
        room = get_chat_room(contact, user)
        chat_rooms.append((contact,room))
    return chat_rooms


def get_chat_room(contact, user):
    contact_owner = User.objects.get(username=contact.phone)
    if contact_owner.id < user.id:
        room = str(contact_owner.id) + 'A' + str(user.id)
    else:
        room = str(user.id) + 'A' + str(contact_owner.id)
    return room


def get_active_contact_username(user_id, chat_room):
    active_contact_id = get_active_contact_id(user_id, chat_room)
    active_contact_username = get_object_or_404(User, id = active_contact_id).username
    return active_contact_username


def get_active_contact_id(user_id, chat_room):
    id_list = chat_room.split('A')
    if int(id_list[0]) == user_id:
        active_user_id = int(id_list[1])
    else:
        active_user_id = int(id_list[0])
    return active_user_id


def update_last_message(user_id, chat_room, message):
    active_contact_id = get_active_contact_id(user_id,chat_room)
    user = get_object_or_404(User,id=user_id)
    active_user = get_object_or_404(User, id=active_contact_id)
    contact1 = get_object_or_404(Contact, user=user, phone=active_user.username)
    contact2 = get_object_or_404(Contact, user=active_user, phone=user.username)
    contact1.last_message = message
    contact2.last_message = message
    contact1.save()
    contact2.save()


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
                texts.append(message)
        texts_list.append((message_date, texts))
    return texts_list










