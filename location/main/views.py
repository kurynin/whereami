from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.files import File
from main.forms import UploadForm, LoginForm, RegisterForm, UploadAntennes
from main.models import Request, Result, Status, Antennes
from main.tasks import process
from django.http import HttpResponse


@require_GET
def home(request):
    msg = request.GET.get('msg', '')

    if request.user.is_authenticated:
        form = UploadForm()

        last_submits_list = list(
            Request.objects
            .filter(user=request.user)
            .order_by('creation_date')
        )

        for sub in last_submits_list:
            if sub.status.name == 'finished':
                res = list(Result.objects.filter(request_id=sub.id).values_list('id', flat=True))
                if res:
                    sub.res = res[0]
                else:
                    sub.res = ''

        return render(request, 'upload.html', context={'form': form,
                                                       'msg': msg,
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
    form = UploadForm(request.POST, request.FILES)

    if form.is_valid():
        antenna = form.cleaned_data['antenna']
        file = form.cleaned_data['file']
        user = request.user

        status = list(Status.objects.filter(name="processing"))

        req = Request.objects.create(user=user, antenna=antenna.name, file=file, status=status[0])

        req.save()

        process(req.id)

        return redirect('/')
    else:
        return redirect('/?msg=invalid request')


@require_GET
def result(request):
    result_id = request.GET.get('result_id', '')

    if result_id:
        res = list(Result.objects.filter(id=result_id))
        res = res[0]

        return render(request, 'results.html', context={'result_id': result_id,
                                                        'pdf_url': res.path_to_pdf,
                                                        'csv_url': res.path_to_csv,
                                                        })
    else:
        return redirect('/')


@login_required
def upload_antennes(request):
    if request.method == 'GET':
        if not request.user.is_superuser:
            return redirect('/')

        form = UploadAntennes()

        return render(request, 'upload_antennes.html', context={'form': form})
    elif request.method == 'POST':
        form = UploadAntennes(request.POST, request.FILES)

        if form.is_valid():
            Antennes.objects.all().delete()

            file = form.cleaned_data['file']

            Antennes.objects.bulk_create([
                Antennes(name=line.decode('utf-8').strip())
                for line in file
            ])

        return redirect('/upload_antennes')
