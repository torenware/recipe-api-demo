FROM python:3.6-alpine
LABEL maintainer="rob@torenware.com (Rob Thorne)"

# Recommended for using python docker images:
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev

RUN pip install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app 

# Create a user account w/o a home dir:
RUN adduser -D user
USER user 



