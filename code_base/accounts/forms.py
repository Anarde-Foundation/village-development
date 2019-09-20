from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

CHOICES= [
    ('Admin', 'Admin'),
    ('Anarde_user', 'Anarde user'),
    ('Anganwadi_worker', 'Anganwadi worker'),
    ('Funder', 'Funder'),
    ]

class UsersRegisterForm(UserCreationForm):

    groups = forms.CharField(label='User role', widget=forms.Select(choices=CHOICES))
    class Meta:
        model = User
        fields = ('username', 'groups', 'password1', 'password2', )

class UpdateUserForm(forms.ModelForm):
    User_CHOICES = [
        ('1', 'True'),
        ('0', 'False'),
    ]
    is_active = forms.CharField(label='Active_status', widget=forms.Select(choices=User_CHOICES))
    class Meta:
         model = User
         fields = ('username', 'is_active')