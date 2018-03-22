FROM ubuntu:latest
MAINTAINER Perseids Project "perseids@tufts.edu"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential mongodb netcat
ADD ./ /app
WORKDIR /app
RUN ls -la
RUN pip3 install -r requirements.txt
CMD ["python3", "run.py"]
