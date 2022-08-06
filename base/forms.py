from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room,User
# from django.contrib.auth.models import User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']

class RoomForm(ModelForm):
    class Meta:
        model=Room
        #de esta manera se basa en el modelo Room para darnos el form
        fields='__all__'
        #para evitar que estos 2 campos se muestren
        exclude=['host','participants']

class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['avatar','name','username','email','bio']