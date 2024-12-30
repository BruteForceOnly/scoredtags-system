FROM python:3

WORKDIR /staticfiles

WORKDIR /app

RUN python -m pip install Django
RUN python -m pip install gunicorn
RUN python -m pip install psycopg[binary]

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "scoredtags.wsgi"]