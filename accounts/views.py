from django.shortcuts import render, redirect
from accounts.forms import RegisterForm
from chat.views import add_chat_rooms
from django.contrib import auth


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()

    else:
        form = RegisterForm()

    return render(request, 'accounts/Signup.html', {"form": form})



def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('login')
