FROM ubuntu:latest

WORKDIR /home/arnov

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip


RUN pip3 install --upgrade pip

RUN pip3 install eudata-server==0.1.23

ENV PATH="${PATH}:/var/lib/docker/.local/bin"

ENTRYPOINT [ "srv prod" ]