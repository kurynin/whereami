# where am i

### Требования
0. Linux (пока что)
1. Python 3.5
2. Django 2.1.5
3. Библиотека huey для асинхронных задач
```
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install django
sudo pip install huey
sudo pip install redis
sudo pip install gevent
```

### Запуск
При первом запуске необходимо обновить структуру базы данных и создать суперюзера, для
входа в панель администрирования:
```
python whereami/location/manage.py makemigrations
python whereami/location/manage.py migrate
python whereami/location/manage.py createsuperuser
```

Для запуска сервера необходимо выполнить:
```
python whereami/location/manage.py runserver
```

Сервер будет доступен по адресу <http://127.0.0.1:8000/>.

Также необходимо запустить в соседнем терминале huey:
```
python whereami/location/manage.py run_huey
```

### Администрирование
Админпанель находится по адресу <http://127.0.0.1:8000/admin> (логиниться с помощью созданного суперюзера).
Из неё можно посмотреть на базу данных. На данный момент интересны таблицы:

Table name | Description
--- | ---
Users | Зарегистрированные пользователи
Requests | Записи о посылках
Statuss | Существующие на данный момент статусы обработки (добавляются вручную администратором)
Results | Записи о результатах обработки

Для полноценной работы необходимой зайти в таблицу Statuss и создать две записи:
1) name = processing, description = какое сообщение будет показываться пользователю в момент обработки,
2) name = finished, description = сообщение по окончанию обработки.

### Текущий статус
Реализована логика с регистрацией пользователей.
После входа пользователь может заполнить простую форму и прикрепить файл. На данный момент реализованная заглушка работы движка, поэтому для корректной обработки файл должен содержать одно число типа int. 
Нажав на кнопку Upload, файл загрузится на сервер, где начнет обрабатываться в фоне. Пользователь будет перенаправлен на текущую страницу, где сможет наблюдать за статусом обработки файла. Как только файл будет обработан, он сможет скачать результат на странице result. Также по окончанию фонового процесса обработки будет отправлено письмо на почту с результатами.

### Ближайшие планы
Кастомизировать свой дизайн для форм.
Улучшить существующий дизайн сайта.
Соптимизировать обращение к БД во время обработки.
Добавить более реальную заглушку движка.
Добавить еще полей в форму загрузки.
