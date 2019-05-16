from django.shortcuts import render,redirect,get_object_or_404
from .models import Contact, Message
from django.contrib.auth.models import User
import operator


def show_contacts(request):
    if request.method == 'POST':
            f = checkuser(request.POST['current_user'])
            if f[2] == '0 contacts':
                return render(request, 'contacts/allcontacts.html',
                              {'count': f[2], 'uname': f[0].first_name, 'message': 'No contacts found', 'user': f[0].username})
            else:
                return render(request,'contacts/allcontacts.html',{'count':f[2], 'uname':f[0].first_name,'mycontacts':f[1],'user':f[0].username})

    return render(request, 'home.html')


def add_contact(request, user):
    if request.method=='POST':
        if request.POST['phone'] != "" and request.POST['name'] != "":
            try:
                Contact.objects.get(phone=request.POST['phone'],user=user)
                f=checkuser(user)
                return render(request, 'contacts/allcontacts.html',
                              {'count': f[2], 'user': f[0].username, 'uname':f[0].first_name, 'mycontacts': f[1],
                               'add': 'yes','error':'That number already exists in your contacts',})
            except Contact.DoesNotExist:
                new_contact = Contact(user=user,phone=request.POST['phone'],name=request.POST['name'],last_message="")
                new_contact.save()
                f = checkuser(user)
                return render(request, 'contacts/allcontacts.html',
                              {'count': f[2], 'user': f[0], 'uname':f[0].first_name, 'mycontacts': f[1],
                               'user_phone': user})
        else:
            f= checkuser(user)
            return render(request, 'contacts/allcontacts.html',
                          {'count': f[2], 'user': f[0].username, 'uname':f[0].first_name, 'mycontacts': f[1],
                           'add': 'yes','error': 'All fields reqiured'})

    f=checkuser(user)
    return render(request, 'contacts/allcontacts.html',
                  {'count': f[2], 'uname': f[0].first_name, 'mycontacts': f[1],
                   'user': f[0].username, 'add':'yes'})


def delete_contact(request):
    pass


def updtate_contact(request):
    pass


def start_chat(request):
    if request.method=='POST':
        texts = get_texts(request.POST['contact_id'],request.POST['user_id'])
        active_contact = get_object_or_404(Contact, phone=request.POST['contact_id'],user=request.POST['user_id'])
        f=checkuser(request.POST['user_id'])
        return render(request, 'contacts/allcontacts.html',
                      {'count': f[2], 'uname': f[0].first_name, 'mycontacts': f[1], 'user': f[0].username,'texts':texts,'contact':active_contact})


def send_message(request):
    if request.method== 'POST':
        new_message = Message(content=request.POST['message'],sender=request.POST['user_id'],receiver=request.POST['contact_id'])
        new_message.save()
        active_contact = get_object_or_404(Contact, phone=request.POST['contact_id'],user=request.POST['user_id'])
        texts = get_texts(request.POST['contact_id'],request.POST['user_id'])
        f=checkuser(request.POST['user_id'])
        return render(request, 'contacts/allcontacts.html',
                      {'count': f[2], 'uname': f[0].first_name, 'mycontacts': f[1], 'user': f[0].username,
                       'texts': texts, 'contact': active_contact})


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

    mylist = [current_user,mycontacts,num]
    return mylist


def get_texts(contact_id,user_id):
    received_messages = Message.objects.filter(sender=contact_id, receiver=user_id)
    sent_messages = Message.objects.filter(sender=user_id, receiver=contact_id)
    list1 = [message for message in received_messages]
    list2 = [message for message in sent_messages]
    all_messages = list1 + list2
    if len(all_messages) == 0:
        return "Null"
    else:
        messages_dict = {}
        for message in all_messages:
            messages_dict.update({message: message.time})

        return sorted(messages_dict.items(), key=operator.itemgetter(1), reverse=False)


