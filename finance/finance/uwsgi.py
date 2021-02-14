[uwsgi]
chdir = .
module = finance.wsgi:application
env = DJANGO_SETTINGS_MODULE=finance.settings
uid = 1000
master = true
threads = 2
processes = 4
