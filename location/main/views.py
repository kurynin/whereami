from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.views.decorators.http import require_GET, require_POST
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from main.forms import UploadForm, LoginForm, RegisterForm
from main.models import Request


@require_GET
def home(request):
    msg = request.GET.get('msg', '')

    if request.user.is_authenticated:
        form = UploadForm()

        last_submits_list = list(
            Request.objects
            .filter(user=request.user)
            .order_by('creation_date')
            .values_list('text', flat=True)
        )

        last_result = request.GET.get('result', '')

        return render(request, 'upload.html', context={'form': form, 'msg': msg,
                                                       'last_result': last_result,
                                                       'last_submits_list': last_submits_list})
    else:
        form = LoginForm()

        return render(request, 'login.html', context={'form': form, 'msg': msg})


@require_POST
def login(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            return redirect('/?msg=incorrect email or password')
    else:
        return redirect('/?msg=check fields')


def register(request):
    if request.method == 'GET':
        form = RegisterForm()

        msg = request.GET.get('msg', '')

        return render(request, 'register.html', context={'form': form, 'msg': msg})
    else:
        form = RegisterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=email).exists():
                return redirect('/register/?msg=username already taken')

            user = User.objects.create_user(username=email, email=email, password=password)

            auth_login(request, user)
            return redirect('/')
        else:
            return redirect('/register/?msg=check fields')


@login_required
@require_POST
def logout(request):
    auth_logout(request)
    return redirect('/')


@login_required
@require_POST
def upload(request):
    form = UploadForm(request.POST)

    if form.is_valid():
        text = form.cleaned_data['text']
        user = request.user

        # Engine simulator :)
        reversed_text = text[::-1]

        req = Request.objects.create(user=user, text=text, result=reversed_text)

        send_mail(
            'Result',
            'Your result: ' + reversed_text,
            'testtopcon@yandex.ru',
            ['kidrachev2011@gmail.com']
        )

        return redirect('/?result=' + reversed_text)
    else:
        return redirect('/?msg=invalid text')
