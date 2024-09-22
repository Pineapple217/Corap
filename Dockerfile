FROM python:3.11.10-alpine3.20

ARG GIT_COMMIT=unspecified
LABEL org.opencontainers.image.version=$GIT_COMMIT
LABEL org.opencontainers.image.source=https://github.com/Pineapple217/Corap

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
COPY ./src /app

COPY devs.csv /

ENTRYPOINT ["sh", "/entrypoint.sh"]