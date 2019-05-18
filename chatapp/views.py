from django.shortcuts import render,redirect,get_object_or_404
from  contacts.models import Contact,Message
from django.contrib.auth.models import User
import operator
from datetime import date, time, datetime


def show_contacts(request):
    if request.method == 'GET':
        user = request.GET['user']
        f = checkuser(user)
        if not f:
            return render(request, 'home.html',
                          {'count': '0 contacts', 'message': 'You have not added any contact'})
        else:
            return render(request, 'home.html',
                      {'count': f[1], 'mycontacts': f[0]})


def add_contact(request):
    if request.method == 'GET':
        user = request.GET['user']
        f = checkuser(user)
        if not f:
            return render(request, 'home.html',
                          {'count': '0 contacts','message':'You have not added any contact','add': 'yes'})
        return render(request, 'home.html',
                      {'count': f[1], 'mycontacts': f[0], 'add': 'yes'})
    elif request.method=='POST':
        user = request.POST['user']
        try:
            User.objects.get(username=request.POST['phone'])
            if request.POST['phone'] != "" and request.POST['name'] != "":
                try:
                    Contact.objects.get(phone=request.POST['phone'],user=user)
                    f=checkuser(user)
                    return render(request, 'home.html',
                                  {'count': f[1], 'mycontacts': f[0], 'add': 'yes','error':'That number already exists in your contacts',})
                except Contact.DoesNotExist:
                    new_contact = Contact(user=user,phone=request.POST['phone'],name=request.POST['name'],last_message="")
                    new_contact.save()
                    f = checkuser(user)
                    return render(request, 'home.html',
                              {'count': f[1], 'mycontacts': f[0],'add': 'yes'})
            else:
                f= checkuser(user)
                return render(request, 'home.html',
                          {'count': f[1], 'mycontacts': f[0],'add': 'yes','error': 'All fields reqiured'})
        except User.DoesNotExist:
            f = checkuser(user)
            if not f:
                return render(request, 'home.html',
                              {'count': '0 contacts', 'message': 'You have not added any contact' , 'add': 'yes',
                               'error': 'Number not registered with smartchat'})
            else:
                return render(request, 'home.html',
                              {'count': f[1], 'mycontacts': f[0], 'add': 'yes',
                               'error': 'Number not registered with smartchat'})


def delete_contact(request):
    pass


def updtate_contact(request):
    pass


def start_chat(request):
    if request.method=='POST':
        texts = get_texts(request.POST['contact_id'],request.POST['user_id'])
        active_contact = get_object_or_404(Contact, phone=request.POST['contact_id'],user=request.POST['user_id'])
        f=checkuser(request.POST['user_id'])
        myset = set()
        if texts:
            for message, time in texts:
                myset.add(message.date)
            dateset = myset
            if request.POST['page'] == 'chats':
                recent_chats = Contact.objects.filter(user=request.POST['user_id'], last_message__isnull=False)
                chatdict = {}
                for recent_chat in recent_chats:
                    chatdict.update({recent_chat: recent_chat.last_message})
                chatlist = [(contact, text) for contact, text in chatdict.items()]
                if chatlist:
                    return render(request, 'home.html',
                                  {'texts': texts, 'contact': active_contact,
                                   'dateset': dateset, 'today': date.today(), 'recents': chatlist[::-1]})
                else:
                    return render(request, 'home.html',
                                  {'texts': texts, 'contact': active_contact,
                                   'dateset': dateset, 'today': date.today(), 'recents': 'Null'})

            elif request.POST['page'] == 'contacts':
                return render(request, 'home.html',
                              {'count': f[1], 'mycontacts': f[0], 'texts': texts, 'contact': active_contact,
                               'dateset': dateset, 'today': date.today()})

        else:
            if request.POST['page'] == 'chats':
                recent_chats = Contact.objects.filter(user=request.POST['user_id'], last_message__isnull=False)
                chatdict = {}
                for recent_chat in recent_chats:
                    chatdict.update({recent_chat: recent_chat.last_message})
                chatlist = [(contact, text) for contact, text in chatdict.items()]
                if chatlist:
                    return render(request, 'home.html',
                                  {'texts': 'Null', 'contact': active_contact,'recents': chatlist})
                else:
                    return render(request, 'home.html',
                                  {'texts': 'Null', 'contact': active_contact,'recents': 'Null'})

            elif request.POST['page'] == 'contacts':
                return render(request, 'home.html',
                              {'count': f[1], 'mycontacts': f[0], 'texts': 'Null', 'contact': active_contact,})


def send_message(request):
    if request.method== 'POST':
        new_message = Message(content=request.POST['message'],sender=request.POST['user_id'],receiver=request.POST['contact_id'],date = date.today(),time=datetime.now())
        new_message.save()
        active_contact = get_object_or_404(Contact, phone=request.POST['contact_id'],user=request.POST['user_id'])
        active_contact.last_message = request.POST['message']
        active_contact.save()
        texts = get_texts(request.POST['contact_id'],request.POST['user_id'])
        f=checkuser(request.POST['user_id'])
        myset = set()
        for message, time in texts:
            myset.add(message.date)
        dateset = myset
        if request.POST['page'] == 'contacts':
            return render(request, 'home.html',{'count': f[1], 'mycontacts': f[0], 'texts': texts, 'contact': active_contact,'dateset':dateset,'today':date.today()})
        elif request.POST['page'] == 'chats':
            recent_chats = Contact.objects.filter(user=request.POST['user_id'], last_message__isnull=False)
            chatdict = {}
            for recent_chat in recent_chats:
                chatdict.update({recent_chat: recent_chat.last_message})
            chatlist = [(contact, text) for contact, text in chatdict.items()]
            if chatlist:
                return render(request, 'home.html',
                              {'texts': texts, 'contact': active_contact,
                               'dateset': dateset, 'today': date.today(), 'recents': chatlist[::-1]})
            else:
                return render(request, 'home.html',
                              {'texts': texts, 'contact': active_contact,
                               'dateset': dateset, 'today': date.today(), 'recents': 'Null'})


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

    mylist = [mycontacts,num]
    return mylist


def get_texts(contact_id,user_id):
    received_messages = Message.objects.filter(sender=contact_id, receiver=user_id)
    sent_messages = Message.objects.filter(sender=user_id, receiver=contact_id)
    list1 = [message for message in received_messages]
    list2 = [message for message in sent_messages]
    all_messages = list1 + list2
    messages_dict = {}
    for message in all_messages:
        messages_dict.update({message: message.time})

    sorted_by_date =  sorted(messages_dict.items(), key=operator.itemgetter(1), reverse=False)
    new_dict = {}
    for message,date in sorted_by_date:
         new_dict.update({message: message.time})

    sorted_by_time = sorted(new_dict.items(), key=operator.itemgetter(1), reverse=False)

    return sorted_by_time


def home(request,user_id):
        recent_chats = Contact.objects.filter(user=user_id,last_message__isnull=False)
        chatdict ={}
        for recent_chat in recent_chats:
           chatdict.update({recent_chat:recent_chat.last_message})
        chatlist = [(contact,text) for contact,text in chatdict.items()]
        if chatlist:
            return render(request, 'home.html',{'recents':chatlist[::-1]})
        else:
            return render(request, 'home.html', {'recents': 'Null'})


def root(request):
    return render(request,'root.html')
















