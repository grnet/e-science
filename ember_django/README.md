Ember application with Django backend.
---
 
Communication happens through Django REST framework.
Ember application files are inside app folder and django backend files are in backend folder. 

Requirements:
--
sudo pip install Django

sudo pip install djangorestframework

sudo pip install rest_framework_ember

sudo pip install djorm-pgarray

django version: 1.7

A database backend for Django. PostgreSQL was used for the application, but by default the Django configuration uses SQLite.

Ember version and other dependencies 
--
jquery: 1.11.1

handlebars: 1.3.0

ember: 1.7.0

ember-data: 1.0.0-beta.11

How to run locally
--
Correct database settings are needed in backend/settings.py file.
After database setup, go to ember_django/ directory and execute:

python manage.py migrate

python manage.py runserver

Optionally, before the runserver command you can create a django superuser for backend management with:

python manage.py createsuperuser

To start the app, open a browser and hit 127.0.0.1:8000.


