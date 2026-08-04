@echo off
start cmd /k "python manage.py runserver"
start cmd /k "celery -A src worker --loglevel=info -P solo"
start cmd /k "celery -A src beat --loglevel=info"