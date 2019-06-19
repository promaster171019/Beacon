Beacon app
==========

Installation
-----------

Clone repo and move into project folder:
```bash
git clone https://github.com/epyatopal/BEacon.git
cd Beacon
```

Create virtual environment (be sure you have installed python3 on your system):
```bash
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

Init database (for full initialization you can use [this](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) manual):
```bash
psql your_user # e.g.: psql postgres
CREATE DATABASE beacon_db_local owner your_user;
```
Create `settings_local.py` within `beacon` folder.
Put next lines to it:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'beacon_db_local',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```
Replace `beacon_db_local`, `your_user`, `your_password` with your values.

Apply migrations to database:
```bash
python manage.py migrate
```

Load dump to database(you may need to use password for psql user):
```bash
psql beacon_db_local < path/to/dump.sql
```

If you have no dumps or you just want to init empty database then just create one super user to login into the system:
```bash
python manage.py createsuperuser
```

Add a new line to the cron job on your server:
```bash
0 1 * * * $ENV/bin/python $APP_dir/manage.py check_status
```

Now run server:
```bash
python manage.py runserver
```
and login with your user.

There are two routes:
1) localhost:8000/admin
here you can manage all data within application
2) localhost:8000/api-docs
List with API-docs

