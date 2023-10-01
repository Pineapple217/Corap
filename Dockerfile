FROM python:3.11-bullseye

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
COPY ./src /app

COPY devs.csv /

ENTRYPOINT ["sh", "/entrypoint.sh"]