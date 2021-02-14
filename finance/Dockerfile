# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
#FROM tiangolo/uwsgi-nginx:python3.6-alpine3.7
# FROM debian:stretch-slim
FROM ubuntu:18.10

RUN apt-get update && apt-get install -y software-properties-common curl \
     && apt-get update \
     && apt-get install -y python3-pip libssl1.0.0 libssl-dev python3-gdal \
     && update-alternatives --install /usr/bin/python python /usr/bin/python3 10 \
     && update-alternatives --install /usr/bin/pip    pip    /usr/bin/pip3    10 \
     && rm -rf /var/lib/apt/lists/*


#RUN apk update
#RUN apk add gcc libc-dev g++ libffi-dev libxml2 unixodbc-dev freetds
#RUN apk add --update --no-cache g++ gcc libxslt-dev
#RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
#FROM continuumio/miniconda3
RUN apt-get update && apt-get install -y && apt-get -y install sudo \
	curl apt-transport-https debconf-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers and tools
RUN sudo apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools
RUN sudo echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN sudo /bin/bash -c "source ~/.bashrc"

RUN apt-get -y install locales
RUN apt-get -y install unixodbc-dev
RUN apt-get -y install python3-dev

RUN apt-get remove -y curl

LABEL Name=finance Version=0.0.1

#ENV UWSGI_INI uwsgi.ini

RUN mkdir /code
WORKDIR /code
ADD . /code/

RUN chmod g+w finance
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install whitenoise

RUN python manage.py collectstatic --noinput

EXPOSE 8000
COPY entrypoint.sh /code/
WORKDIR /code
ENTRYPOINT ["sh", "entrypoint.sh"]
#CMD python manage.py runserver_plus 0.0.0.0:8000 --cert /tmp/cert
#CMD ["python", "manage.py", "runserver_plus", "0.0.0.0:8000", "--cert", "/tmp/cert"]


# Using pip:
#RUN python -m pip install -r requirements.txt
#CMD python manage.py runserver_plus 0.0.0.0:8000 --cert /tmp/cert
#CMD ["python", "manage.py", "runserver_plus", "0.0.0.0:80", "--cert", "/tmp/cert"]

#CMD ["python3", "-m", "finance"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "finance"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m finance"
# CMD python manage.py runserver 0.0.0.0:8000