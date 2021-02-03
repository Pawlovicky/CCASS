FROM ubuntu:20.04
MAINTAINER Pawlovicky <Pawlovicky@gmail.com>
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    wget \
    zip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN cp chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
RUN apt-get update && apt-get install -f -y
RUN apt-get install -y \
    python3-selenium \
    python3 \
    python3-pip \
    python3-venv \
    vim
RUN pip3 install selenium pandas lxml html5lib bs4 \
         dash numpy
RUN apt-get install -y sudo
RUN adduser --uid 1001 --disabled-password --gecos '' pavel
RUN adduser pavel sudo
RUN mkdir -p /home/pavel
RUN /etc/init.d/dbus start
RUN chown pavel /home/pavel
USER pavel
