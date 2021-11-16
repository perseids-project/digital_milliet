FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential mongodb netcat \
  nodejs npm git

RUN mkdir /app && mkdir /app/digital_milliet
WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY digital_milliet/bower.json /app/digital_milliet/bower.json

RUN npm install -g bower
RUN cd digital_milliet && bower install -f --allow-root
RUN pip3 install -r requirements.txt

ADD . /app

CMD python3 run.py
