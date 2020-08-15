# Notes on Django REST Project

* Set up project

``` bash

$ docker-compose run app  sh -c "django-admin.py startproject app ."
```

* Running tests

``` 
$ docker-compose run app  sh -c "python manage.py test"
```

* Running the migration

``` 
docker-compose run app sh -c "python manage.py makemigrations core"
```

* Create user app

``` bash

$ docker-compose run --rm app  sh -c "python manage.py startapp user"
```
