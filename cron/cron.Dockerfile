FROM python:3

WORKDIR /app
RUN python -m pip install Django
RUN python -m pip install psycopg[binary]
COPY ./scoredtags .

WORKDIR /scripts
COPY ./cron/generate-pepper.py .
COPY ./cron/init.sh .

WORKDIR /ppprs

RUN apt-get update
RUN apt-get install -y cron
COPY ./cron/monthly-pepper-generation /etc/cron.d/monthly-pepper-generation
RUN chmod 0644 /etc/cron.d/monthly-pepper-generation

CMD [ "/bin/bash", "/scripts/init.sh" ]