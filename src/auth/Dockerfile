FROM python:3.12-slim

RUN apt update && apt install -y --no-install-recommends --no-install-suggests\
  build-essential default-libmysqlclient-dev pkg-config \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade pip


WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 5000

CMD ["python3", "server.py"]