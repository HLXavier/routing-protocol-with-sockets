FROM ubuntu

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    net-tools

RUN ln -s /usr/bin/python3 /usr/bin/python

ADD sender.py .