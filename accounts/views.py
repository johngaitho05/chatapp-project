from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from chat.views import add_chat_rooms
from django.contrib import auth


def signup(request):
    if request.method=='POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.get(username=request.POST['phone'])
                return render(request,'accounts/signup.html', {'error': "That phone number has already been registered"})
            except User.DoesNotExist:
                current_user = User.objects.create_user(username=request.POST['phone'],password=request.POST['password1'],first_name=request.POST['fname'],last_name=request.POST['lname'])
                add_chat_rooms(current_user)
                return render(request, 'accounts/login.html',{'message':'Registration successful. Login to continue'})
        else:
            return render(request, 'accounts/signup.html', {'error': "Password do not match"})

    return render(request, 'accounts/signup.html')


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['phone'],password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('homepage')
        else:
            return render(request, 'accounts/login.html',{'error':'Invalid credentials'})
    return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('login')
