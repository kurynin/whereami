from django import forms
from main.models import Antennes


class UploadForm(forms.Form):
    antenna = forms.ModelChoiceField(queryset=Antennes.objects.all(), required=True)
    file = forms.FileField(required=True)


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


RegisterForm = LoginForm


class UploadAntennes(forms.Form):
    file = forms.FileField(required=True)
