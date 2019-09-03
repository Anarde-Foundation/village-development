from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
group = forms.ModelChoiceField(queryset=Group.objects.all(),
                                   required=True)
print ('===========',group)
CHOICES= [
    ('Admin', 'Admin'),
    ('Anarde_user', 'Anarde user'),
    ('Anganwadi_worker', 'Anganwadi worker'),
    ('Funder', 'Funder'),
    ]

class UsersRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    groups = forms.CharField(label='User role', widget=forms.Select(choices=CHOICES))
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'groups', 'password1', 'password2', )