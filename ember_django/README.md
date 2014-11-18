Ember application with Django backend.
---
 
Communication happens through Django REST framework.
2 folders for this project:
  Backend: django
  Frontend: ember (following the ember-cli structure) 

Requirements:
--
    sudo pip install Django
    django version: 1.7

    sudo pip install djangorestframework

    sudo pip install rest_framework_ember

    sudo pip install djorm-pgarray



A database backend for Django. PostgreSQL was used for the application, but by default the Django configuration uses SQLite.

Ember version and other dependencies 
--
    jquery: 1.11.1

    handlebars: 1.3.0

    ember: 1.7.0

    ember-data: 1.0.0-beta.11

for ember-cli (installation is optional at this point)
---
    curl https://raw.githubusercontent.com/creationix/nvm/v0.12.1/install.sh | bash
    
    source ~/.profile

    nvm install [version-no] 

(e.g. nvm install 0.11.13)
 
    npm install -g ember-cli

    npm install -g bower

    npm install -g phantomjs

    nvm alias default [version-no] 
(e.g. nvm alias default v0.11.13)

How to run locally
--
Correct database settings are needed in backend/settings.py file.
After database setup, go to ember_django/ directory and execute:

    python manage.py migrate

    python manage.py runserver

Optionally, before the runserver command you can create a django superuser for backend management with:

    python manage.py createsuperuser

To start the app, open a browser and hit 127.0.0.1:8000.

Important!
---
After the ~okeanos v0.16 update which added the seperation of resources per project, the project id of e-science is needed for the application to run. For the time being, it should be added inside the <projectroot>/.private/.config.txt file, in the following section:


    [cloud "~okeanos"]
    url = okeanos authentication url, needed for the tests
    token = okeanos token, needed for the tests
    project_id = the e-science project id, needed for the ember_django  application to run




	







