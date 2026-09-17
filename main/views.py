from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Room
# Create your views here.


def home_view(request):
    return render(request, "home.html")


@login_required
def chat_view(request):
    slug = request.GET.get('slug', '')
    rooms = Room.objects.all()
    if slug == "":
        room = Room.objects.first()
    else:
        room = Room.objects.get(slug=slug)
    context = {'rooms': rooms, 'room': room}
    return render(request, "chat.html", context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically logs in the new user
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})
