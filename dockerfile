FROM ubuntu:latest

RUN apt-get upgrade
RUN apt-get install -y python3.9
RUN apt-get install -y python3-pip

RUN pip install eudata-server==0.1.21

ENTRYPOINT [ "srv prod" ]