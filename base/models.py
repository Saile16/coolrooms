from email.policy import default
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    name=models.CharField(max_length=255,null=True)
    email=models.EmailField(max_length=55,null=True,unique=True)
    bio=models.TextField(max_length=300,null=True)

    avatar=models.ImageField(null=True,default='avatar.svg')
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

class Topic(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Room(models.Model):
    #un Room solo puede tener un host en este un USER
    host=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    #un Room solo puede tener un topic
    topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=100)
    description=models.TextField(null=True,blank=True)
    participants=models.ManyToManyField(User,related_name='participants',blank=True)
    #cada ves que actualizamos la tabla
    updated= models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True) 

    class Meta:
        #de esta manera los ordenamos por el campo created
        ordering=['-updated','-created']

    def __str__(self):  
        return self.name
    
class Message(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    #aqui decimos en el room se pueden enviar varios mensajes one to many relacion
    room=models.ForeignKey(Room,on_delete=models.CASCADE)
    body=models.TextField()
    updated= models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True) 

    class Meta:
        #de esta manera los ordenamos por el campo created
        ordering=['-updated','-created']
        
    def __str__(self):
        #para que nos muestre solo 0 a 50 caracteres
        return self.body[0:50]