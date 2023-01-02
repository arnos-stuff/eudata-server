FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip


RUN pip3 install --upgrade pip

RUN pip3 install eudata-server==0.1.23

ENTRYPOINT [ "srv prod" ]