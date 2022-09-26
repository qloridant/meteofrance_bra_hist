FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive
ENV FIREFOX_VER 87.0
ENV GECKODRIVER_VERSION=31

RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt install -y \
       firefox-esr \
   && pip install webdriver_manager \
   && wget https://github.com/mozilla/geckodriver/releases/download/v0.${GECKODRIVER_VERSION}.0/geckodriver-v0.${GECKODRIVER_VERSION}.0-linux64.tar.gz \
   && tar -xvzf geckodriver* \
   && chmod +x geckodriver \
   && mv geckodriver /usr/local/bin/
#ENV POETRY_HOME="~"
#RUN curl -sSL https://install.python-poetry.org | python3 -
#ENV PATH="${PATH}:$POETRY_HOME/bin"
RUN pip install poetry
ENV PYTHON="."
