from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth.models import User
from huey.contrib.sqlitedb import SqliteHuey
from main.models import Request, Result, Status
from time import sleep

import subprocess

huey = SqliteHuey('db.sqlite3')

PATH_TO_SOME_TOPCON_INFO = settings.BASE_DIR + '/engine/some_topcon_info.ssr'


def create_ini_file(req):
    f = open(settings.BASE_DIR + '/media/' + req.file.name + '.ini', 'w')

    f.write('RoverFile = ' + req.file.path + '\n')
    f.write('Sp3File = ' + PATH_TO_SOME_TOPCON_INFO + '\n')
    f.write('OutputDir = ' + settings.BASE_DIR + '/media/\n')
    f.write('RoverAntID = ' + req.antenna + '\n')

    f.close()


@huey.task()
def process(request_id):
    sleep(4)

    req = list(Request.objects.filter(id=request_id))
    req = req[0]

    create_ini_file(req)

    sleep(4)

    subprocess.call(
        'g++ ' + settings.BASE_DIR + '/engine/engine.cpp -o ' +
        settings.BASE_DIR + '/engine/a.out', shell=True)

    sleep(4)

    subprocess.call(
        settings.BASE_DIR + '/engine/a.out ' +
        settings.BASE_DIR + '/media/' + req.file.name + '.ini ' +
        req.file.name, shell=True)

    sleep(4)

    user = list(User.objects.filter(id=req.user.id))

    msg = EmailMessage('Result', 'Your result:', 'testtopcon@yandex.ru', [user[0].email])
    msg.content_subtype = "html"
    msg.attach_file(settings.BASE_DIR + '/media/' + req.file.name + '.gga')
    msg.attach_file(settings.BASE_DIR + '/media/' + req.file.name + '.rtk')
    msg.send()

    status = list(Status.objects.filter(name="finished"))

    Result.objects.create(path_to_gga='/media/' + req.file.name + '.gga',
                          path_to_rtk='/media/' + req.file.name + '.rtk',
                          request_id=req)

    Request.objects.filter(user=user[0].id).update(status=status[0])
