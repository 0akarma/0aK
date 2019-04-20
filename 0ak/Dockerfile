FROM python:3.7-slim

COPY . /0ak
WORKDIR /0ak

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["gunicorn", "-c", "/0ak/gunicorn.py", "wsgi:app"]

