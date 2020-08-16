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

* Bring the app up

``` bash
docker-compose up
```

* Test user

killroy@was.here / password-stuff

``` 
{
    "token": "996c1ada28479bc60f0a6907089253a7542e046f"
}
```
