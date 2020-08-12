FROM python:3.6-alpine
LABEL maintainer="rob@torenware.com (Rob Thorne)"

# Recommended for using python docker images:
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app 

# Create a user account w/o a home dir:
RUN adduser -D user
USER user 



