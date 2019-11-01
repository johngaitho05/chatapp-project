from django.shortcuts import render, redirect, get_object_or_404
from contacts.models import Contact, Message
from django.contrib.auth.models import User
import operator
from datetime import date, datetime
from django.utils.safestring import mark_safe
import json


def show_contacts(request):
    if request.method == 'GET':
        user = request.GET['user']
        f = checkuser(user)
        if not f[0]:
            return render(request, 'contacts/home.html',
                          {'count': f[1], 'message': 'You have not added any contact'})
        else:
            return render(request, 'contacts/home.html',
                          {'count': f[1], 'mycontacts': f[0]})


def add_contact(request):
    if request.method == 'GET':
        user = request.GET['user']
        f = checkuser(user)
        if not f[0]:
            return render(request, 'contacts/home.html',
                          {'count': '0 contacts', 'message': 'You have not added any contact', 'add': 'yes'})
        return render(request, 'contacts/home.html',
                      {'count': f[1], 'mycontacts': f[0], 'add': 'yes'})
    elif request.method == 'POST':
        user = request.POST['user']
        try:
            User.objects.get(username=request.POST['phone'])
            if request.POST['phone'] != "" and request.POST['name'] != "":
                try:
                    Contact.objects.get(phone=request.POST['phone'], user=user)
                    f = checkuser(user)
                    return render(request, 'contacts/home.html',
                                  {'count': f[1], 'mycontacts': f[0], 'add': 'yes',
                                   'error': 'That number already exists in your contacts', })
                except Contact.DoesNotExist:
                    new_contact = Contact(user=user, phone=request.POST['phone'], name=request.POST['name'],
                                          last_message="")
                    new_contact.save()
                    f = checkuser(user)
                    return render(request, 'contacts/home.html',
                                  {'count': f[1], 'mycontacts': f[0], 'add': 'yes'})
            else:
                f = checkuser(user)
                return render(request, 'contacts/home.html',
                              {'count': f[1], 'mycontacts': f[0], 'add': 'yes', 'error': 'All fields reqiured'})
        except User.DoesNotExist:
            f = checkuser(user)
            if not f[0]:
                return render(request, 'contacts/home.html',
                              {'count': '0 contacts', 'message': 'You have not added any contact', 'add': 'yes',
                               'error': 'Number not registered with smartchat'})
            else:
                return render(request, 'contacts/home.html',
                              {'count': f[1], 'mycontacts': f[0], 'add': 'yes',
                               'error': 'Number not registered with smartchat'})


def delete_contact(request):
    pass


def updtate_contact(request):
    pass


def start_chat(request):
    if request.method == 'POST':
        texts = get_texts(request.POST['contact_id'], request.POST['user_id'])
        active_contact = get_object_or_404(Contact, phone=request.POST['contact_id'], user=request.POST['user_id'])
        f = checkuser(request.POST['user_id'])
        if texts:
            textlist = create_chat_set(texts)
            if request.POST['page'] == 'chats':
                chatlist = get_chatlist(request.POST['user_id'])
                if len(chatlist) > 0:
                    return render(request, 'contacts/home.html',
                                  {'texts': texts, 'contact': active_contact,
                                   'textlist': textlist[::-1], 'today': date.today(), 'recents': chatlist[::-1]})
                else:
                    return render(request, 'contacts/home.html',
                                  {'texts': texts, 'contact': active_contact,
                                   'textlist': textlist, 'today': date.today(), 'recents': 'Null'})

            elif request.POST['page'] == 'contacts':
                return render(request, 'contacts/home.html',
                              {'count': f[1], 'mycontacts': f[0], 'texts': texts, 'contact': active_contact,
                               'textlist': textlist[::-1], 'today': date.today()})

        else:
            if request.POST['page'] == 'chats':
                recent_chats = Contact.objects.filter(user=request.POST['user_id'], last_message__isnull=False)
                chatdict = {}
                for recent_chat in recent_chats:
                    chatdict.update({recent_chat: recent_chat.last_message})
                chatlist = [(contact, text) for contact, text in chatdict.items()]
                if chatlist:
                    return render(request, 'contacts/home.html',
                                  {'textlist': 'Null', 'contact': active_contact, 'recents': chatlist[::-1]})
                else:
                    return render(request, 'contacts/home.html',
                                  {'textlist': 'Null', 'contact': active_contact, 'recents': 'Null'})

            elif request.POST['page'] == 'contacts':
                return render(request, 'contacts/home.html',
                              {'count': f[1], 'mycontacts': f[0], 'textlist': 'Null', 'contact': active_contact, })


def send_message(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        contact_id = request.POST['contact_id']
        message = request.POST['message']
        page = request.POST['page']
        if message != "":
            new_message = Message(content=message, sender=user_id,receiver=contact_id, date=date.today(), time=datetime.now())
        else:
            new_message = Message(content="No content", sender=user_id,receiver=contact_id, date=date.today(), time=datetime.now())
        new_message.save()
        user1 = get_object_or_404(Contact, phone=contact_id, user=user_id)
        user2 = get_object_or_404(Contact, phone=user_id, user=contact_id)
        if message != "":
            user1.last_message = message
            user2.last_message = message
        else:
            user1.last_message = "(No content)"
            user2.last_message = "(No content)"
        user1.save(update_fields=["last_message"])
        user2.save(update_fields=["last_message"])
        return render(request, 'contacts/home.html',generate_valsdict(user_id,contact_id,page))


def home(request, user_id):
    chatlist = get_chatlist(user_id)
    if len(chatlist) > 0:
        return render(request, 'contacts/home.html', {'recents': chatlist[::-1]})
    else:
        return render(request, 'contacts/home.html', {'recents': 'Null'})


def root(request):
    return render(request, 'contacts/root.html')


def checkuser(user):
    current_user = User.objects.get(username=user)
    mycontacts = Contact.objects.filter(user=current_user)
    count = []
    for contact in mycontacts:
        count.append(contact)
    if len(count) == 1:
        num = '1 contact'
    else:
        num = str(len(count)) + ' contacts'

    mylist = [mycontacts, num]
    return mylist


def get_texts(contact_id, user_id):
    received_messages = Message.objects.filter(sender=contact_id, receiver=user_id)
    sent_messages = Message.objects.filter(sender=user_id, receiver=contact_id)
    list1 = [message for message in received_messages]
    list2 = [message for message in sent_messages]
    all_messages = list1 + list2
    messages_dict = {}
    for message in all_messages:
        messages_dict.update({message: message.time})

    sorted_by_date = sorted(messages_dict.items(), key=operator.itemgetter(1), reverse=False)
    new_dict = {}
    for message, date in sorted_by_date:
        new_dict.update({message: message.time})

    sorted_by_time = sorted(new_dict.items(), key=operator.itemgetter(1), reverse=False)

    return sorted_by_time


# returns a sorted list of texts
def create_chat_set(texts):
    myset = set()
    for message, time in texts:
        myset.add(message.date)
    dateset = myset
    biglist = []
    for mdate in dateset:
        mylist = []
        for message, time in texts:
            if message.date == mdate:
                mylist.append((message, time))
        biglist.append((mdate, mylist))
    return biglist


# returns a list of recent chats to display on the homepage
def get_chatlist(user):
    recent_chats = Contact.objects.filter(user=user)
    chatdict = {}
    for recent_chat in recent_chats:
        chatdict.update({recent_chat: recent_chat.last_message})
    chatlist = []
    for contact, text in chatdict.items():
        if text != '':
            if len(text) > 40:
                chatlist.append((contact, text[:40] + '...'))
            else:
                chatlist.append((contact, text))

    return chatlist


# returns a dictionary of values that dictates how the homepage will look like
def generate_valsdict(user_id,contact_id,page):
    active_contact = get_object_or_404(Contact, phone=contact_id, user=user_id)
    texts = get_texts(contact_id,user_id)
    f = checkuser(user_id)
    textlist = create_chat_set(texts)
    if page == 'contacts':
          valsdict = {'count': f[1], 'mycontacts': f[0], 'contact': active_contact, 'textlist': textlist[::-1],
                       'today': date.today()}
    else :
        chatlist = get_chatlist(user_id)
        if len(chatlist) > 0:
            valsdict = {'texts': texts, 'contact': active_contact,
                           'textlist': textlist[::-1], 'today': date.today(), 'recents': chatlist[::-1]}
        else:
            valsdict = {'texts': texts, 'contact': active_contact,
                           'textlist': textlist[::-1], 'today': date.today(), 'recents': 'Null'}
        return valsdict











