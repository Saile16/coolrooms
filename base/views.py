import email
from pydoc_data.topics import topics
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#este import Q nos permite tener busquedas dinamicas como OR en Django
from django.db.models import Q
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
# from django.contrib.auth.forms import UserCreationForm

# from django.http import HttpResponse
from .models import Message, Room,Topic,User
from .forms import RoomForm,UserForm,MyUserCreationForm
# Create your views here.

# rooms=[
#     {'id':1,'name':'Lets learn python!!'},
#     {'id':2,'name':'Lets learn JS!!'},
#     {'id':3,'name':'Lets learn django!!'},
# ]

#AUTH USER
def login_page(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')  

    if request.method=='POST':
        email=request.POST.get('email').lower()
        # username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request,'User not found or does not exist')
        
        user=authenticate(request,email=email,password=password)
        # user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username OR password doest not exist')

    context={
        'page':page
    }
    return render(request,'base/login_register.html',context)

def logout_page(request):
    logout(request)
    return redirect('home')

def register_page(request):
    # page='register'
    form = MyUserCreationForm()
    if request.method== 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error has ocurred')
    context={
        'form':form,
    }
    return render(request,'base/login_register.html',context)

#CRUD Y VISTAS
def home(request):
    #traemos todos los rooms de la base de datos    
    # rooms=Room.objects.all()
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    # rooms=Room.objects.filter(topic__name__icontains=q)
    rooms=Room.objects.filter(Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
    )
    #para obtener cierta cantidad de topics no todos
    topics=Topic.objects.all()[0:5]
    #para contar todos los room de la base de datos
    room_count=rooms.count()
    # room_messages=Message.objects.all()
    room_messages=Message.objects.filter(Q( room__topic__name__icontains=q))

    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request, 'base/home.html',context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    #Aca decimos que nos den todos los messages que estan atados a este room
    # room_messages=room.message_set.all().order_by('-created')
    room_messages=room.message_set.all()
    #recordar que los participants tiene relacion many to many
    #los agregamos dentro del admin por ahora
    participants=room.participants.all()
    if request.method=='POST':
        #creamos el mensaje de esta manera llamando a model Message
        message=Message.objects.create(
            #pasamos sus valores
            user=request.user,
            room=room,
            #obtenemos el mensaje del form de message con name='body'
            body=request.POST.get('body')
        )
        #de esta manera agregamos al user que comenta dentro de participants
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context={'room':room,'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html',context)

#userprofile
def user_profile(request,pk):
    user=User.objects.get(id=pk)    
    #obtenemos todos los rooms que estan atados a este user
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics
    }
    return render(request, 'base/profile.html',context)

@login_required(login_url='login')
def create_room(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        #creamos el room de esta manera llamando a model Room
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
        #recibimos el formulario
        # form=RoomForm(request.POST)
        #si el formulario es valido si pasaron bien los datos los grabamos
        # if form.is_valid():
        #     room=form.save(commit=False)
        #     #para que grabemos el usuario que ha creado el room
        #     room.host=request.user
        #     room.save()
            # return redirect('home')
    context={
        'form':form,
        'topics':topics
    }
    
    return render(request, 'base/room_form.html',context)


@login_required(login_url='login')
def update_room( request,pk):
    room=Room.objects.get(id=pk)
    #tenemos que llamar el formulario con los datos de la room que obtuvimos
    form=RoomForm(instance=room)
    topics=Topic.objects.all()
    #bloqueamos el acceso a al user que no es dueño de la sala
    if request.user !=room.host:
        return HttpResponse('You are not authorized to edit this room')
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        #recibimos el form y tambien decimos que room necesitamos
        # form=RoomForm(request.POST,instance=room)
        # if form.is_valid():
        #     form.save()
            # return redirect('home')

    context={
        'form':form,
        'topics':topics,
        'room':room
    }
    return render(request,'base/room_form.html',context)

#tanto en deleteroom como en delete_message usamos el contexto "dinamicamente"
#mandandolo como obj
@login_required(login_url='login')
def delete_room(request,pk):
    room=Room.objects.get(id=pk)
    #bloqueamos el acceso a al user que no es dueño de la sala
    if request.user !=room.host:
        return HttpResponse('You are not authorized to edit this room')
    if request.method=='POST':
        room.delete()
        return redirect('home')
   
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')
def delete_message(request,pk):
    message=Message.objects.get(id=pk)
    #bloqueamos el acceso a al user que no es dueño de la sala
    if request.user !=message.user:
        return HttpResponse('You are not authorized to edit this message')
    if request.method=='POST':
        message.delete()
        return redirect('home')
    
    return render(request,'base/delete.html',{'obj':message})

@login_required(login_url='login')
def update_user(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method=='POST':
        form=UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    return render(request,'base/update_user.html',{'form':form})

def topics_page(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})
    
def activity_page(request):
    room_messages=Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})