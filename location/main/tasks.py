from statistics import variance

from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from huey.contrib.sqlitedb import SqliteHuey
from main.models import Request, Result, Status
from time import sleep
from math import sin, cos, sqrt, pi

import subprocess
import latex
import logging

huey = SqliteHuey('db.sqlite3')

PATH_TO_SOME_TOPCON_INFO = settings.BASE_DIR + '/engine/some_topcon_info.ssr'

E2 = 0.00669437999014
OME2 = 0.99330562000987
A = 6378137.0
EPS = 1e-7

GGA_STR = '$GPGGA'
GGA_TYPE = 0
GGA_TIME = 1
GGA_LATITUDE = 2
GGA_LAT_SIGN = 3
GGA_LONGITUDE = 4
GGA_LON_SIGN = 5
GGA_CONV = 6
GGA_SPUTNIK = 7
GGA_HIGH = 9
GGA_HIGH_ADD = 11

logger = logging.getLogger(__name__)


def create_ini_file(req):
    f = open(settings.BASE_DIR + '/media/' + req.file.name + '.ini', 'w')

    f.write(render_to_string('ini_template', context={'file_name': req.file.path,
                                                      'some_topcon_info': PATH_TO_SOME_TOPCON_INFO,
                                                      'output_dir': settings.BASE_DIR + '/media/',
                                                      'antenna': req.antenna}))
    f.close()


def create_csv_file(req, x, y, z, x_cov, y_cov, z_cov):
    f = open(settings.BASE_DIR + '/media/' + req.file.name + '.csv', 'w')

    f.write(render_to_string('csv_template', context={'X': x,
                                                      'Y': y,
                                                      'Z': z,
                                                      'X_COV': x_cov,
                                                      'Y_COV': y_cov,
                                                      'Z_COV': z_cov}))
    f.close()


def create_tex_file(req, x, y, z, x_cov, y_cov, z_cov, x_arr, y_arr, z_arr, sputniks, time_in_sec):
    x_min = min(x_arr)
    y_min = min(y_arr)
    z_min = min(z_arr)
    x_max = max(x_arr)
    y_max = max(y_arr)
    z_max = max(z_arr)

    for i in range(len(x_arr)):
        x_arr[i] = (time_in_sec[i], (x_arr[i] - x_min) / (x_max - x_min + EPS))

    for i in range(len(y_arr)):
        y_arr[i] = (time_in_sec[i], (y_arr[i] - y_min) / (y_max - y_min + EPS))

    for i in range(len(z_arr)):
        z_arr[i] = (time_in_sec[i], (z_arr[i] - z_min) / (z_max - z_min + EPS))

    for i in range(len(sputniks)):
        sputniks[i] = (time_in_sec[i], sputniks[i])

    tex_text = render_to_string('tex_template', context={'X': x,
                                                         'Y': y,
                                                         'Z': z,
                                                         'X_COV': x_cov,
                                                         'Y_COV': y_cov,
                                                         'Z_COV': z_cov,
                                                         'X_ARR': x_arr,
                                                         'Y_ARR': y_arr,
                                                         'Z_ARR': z_arr,
                                                         'sputniks': sputniks,
                                                         'time': time_in_sec,
                                                         'TIME_MIN': min(time_in_sec),
                                                         'TIME_MAX': max(time_in_sec)})

    logger.warning(tex_text)

    f = open(settings.BASE_DIR + '/media/' + req.file.name + '.tex', 'w')

    f.write(tex_text)

    f.close()

    latex.build_pdf(tex_text).save_to(settings.BASE_DIR + '/media/' + req.file.name + '.pdf')


def convert_to_xyz(lon, lat, hgt):
    slat = sin(lat)
    clat = cos(lat)
    slon = sin(lon)
    clon = cos(lon)
    n = A / sqrt(1.0 - E2 * slat * slat)
    nph = n + hgt
    x = nph * clat * clon
    y = nph * clat * slon
    z = (OME2 * n + hgt) * slat
    return x, y, z


def parse_time(tm):
    hh = int(tm[0:2])
    mm = int(tm[2:4])
    ss = int(tm[4:6])
    sec = hh * 3600 + mm * 60 + ss
    return sec


def parse_coord(coord, is_lat):
    grad = float(coord[0:3 - is_lat])
    grad += float(coord[3 - is_lat:]) / 60.0
    return grad / 180.0 * pi


def process_gga(req):
    with open(settings.BASE_DIR + '/media/' + req.file.name + '.gga') as f:
        x = 0.0
        y = 0.0
        z = 0.0
        x_arr = []
        y_arr = []
        z_arr = []
        x_conv = []
        y_conv = []
        z_conv = []
        sputniks = []
        time_in_sec = []
        time_offset = 0

        for line in f:
            columns = line.split(',')
            if not columns or columns[GGA_TYPE] != GGA_STR:
                continue
            lat = parse_coord(columns[GGA_LATITUDE], True)
            lon = parse_coord(columns[GGA_LONGITUDE], False)
            high = float(columns[GGA_HIGH]) + float(columns[GGA_HIGH_ADD])

            if columns[GGA_LAT_SIGN] == 'S':
                lat *= -1

            if columns[GGA_LON_SIGN] == 'W':
                lon *= -1

            xyz = convert_to_xyz(lon, lat, high)

            if columns[GGA_CONV] == '5':
                x += xyz[0]
                y += xyz[1]
                z += xyz[2]

                x_conv.append(xyz[0])
                y_conv.append(xyz[1])
                z_conv.append(xyz[2])

            x_arr.append(xyz[0])
            y_arr.append(xyz[1])
            z_arr.append(xyz[2])
            sputniks.append(int(columns[GGA_SPUTNIK]))
            time_in_sec.append(parse_time(columns[GGA_TIME]) + time_offset)

            if len(time_in_sec) > 1 and time_in_sec[-1] < time_in_sec[-2]:
                time_offset += 3600 * 24
                time_in_sec[-1] += time_offset

        x /= len(x_conv)
        y /= len(y_conv)
        z /= len(z_conv)

        x_cov = variance(x_conv, x)
        y_cov = variance(y_conv, y)
        z_cov = variance(z_conv, z)

        create_tex_file(req, x, y, z, x_cov, y_cov, z_cov, x_arr, y_arr, z_arr, sputniks, time_in_sec)
        create_csv_file(req, x, y, z, x_cov, y_cov, z_cov)


@huey.task()
def process(request_id):
    sleep(1)

    req = list(Request.objects.filter(id=request_id))
    req = req[0]

    create_ini_file(req)

    # sleep(3)
    # subprocess.call(
    #    'g++ ' + settings.BASE_DIR + '/engine/engine.cpp -o ' +
    #    settings.BASE_DIR + '/engine/a.out', shell=True)

    sleep(3)

    subprocess.call(
        settings.BASE_DIR + '/engine/a.out ' +
        settings.BASE_DIR + '/media/' + req.file.name + '.ini ' +
        req.file.name, shell=True, cwd=settings.BASE_DIR + '/engine/')

    sleep(3)

    process_gga(req)

    sleep(3)

    user = list(User.objects.filter(id=req.user.id))

    msg = EmailMessage('Result', 'Your result:', settings.EMAIL_HOST_USER, [user[0].email])
    msg.content_subtype = "html"
    msg.attach_file(settings.BASE_DIR + '/media/' + req.file.name + '.pdf')
    msg.attach_file(settings.BASE_DIR + '/media/' + req.file.name + '.csv')
    msg.send()

    status = list(Status.objects.filter(name="finished"))

    Result.objects.create(path_to_pdf='/media/' + req.file.name + '.pdf',
                          path_to_csv='/media/' + req.file.name + '.csv',
                          request_id=req)

    Request.objects.filter(user=user[0].id).update(status=status[0])
