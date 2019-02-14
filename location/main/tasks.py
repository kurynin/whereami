from huey.contrib.sqlitedb import SqliteHuey
from location.main.models import TMP
from time import sleep

huey = SqliteHuey('db.sqlite3')


@huey.task()
def wait():
    TMP.objects.create(text="test")

