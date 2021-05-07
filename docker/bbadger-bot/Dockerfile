FROM python:3.8-alpine3.13

WORKDIR /BadgerDiscordBot

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apk add --no-cache \
        libressl-dev \
        musl-dev \
        gcc \
        make \
        libffi-dev 

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apk del \
        libressl-dev \
        musl-dev \
        gcc \
        make \
        libffi-dev

COPY . .

CMD [ "python", "scripts/run_bbadger_bot.py" ]