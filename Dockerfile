FROM python:3

ADD . /baas
WORKDIR /baas

RUN pip install poetry && \
    poetry install

WORKDIR ./baas

CMD ["python", "-m", "poetry", "run", "gunicorn", "app:app"]
