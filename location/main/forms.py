from django import forms


CHOICES_ANTENS = (
    (1, 'antenna_01'),
    (2, 'antenna_02'),
    (3, 'antenna_03'),
    (4, 'antenna_04'),
    (5, 'antenna_05'),
)


class UploadForm(forms.Form):
    antenna = forms.ChoiceField(choices=CHOICES_ANTENS)
    file = forms.FileField(required=True)


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


RegisterForm = LoginForm


class GetFileURL(forms.Form):
    file = forms.FileField()