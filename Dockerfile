FROM python:3.11-bullseye

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

ADD crontab /etc/cron.d/corap
RUN touch /var/log/cron.log
RUN chmod 0644 /etc/cron.d/corap

RUN apt-get update
RUN apt-get -y install cron

COPY entrypoint.sh /entrypoint.sh
COPY ./src /app

ENTRYPOINT ["sh", "/entrypoint.sh"]