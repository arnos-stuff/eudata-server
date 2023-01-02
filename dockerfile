FROM python:3.8.10

RUN apt-get upgrade
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install --upgrade pip

RUN pip install eudata-server==0.1.21

ENTRYPOINT [ "srv prod" ]