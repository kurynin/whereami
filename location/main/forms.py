from django import forms


class UploadForm(forms.Form):
    text = forms.CharField(max_length=80)


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


RegisterForm = LoginForm
