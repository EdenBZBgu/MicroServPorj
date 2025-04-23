FROM python:3.12-slim

RUN apt update && apt install -y --no-install-recommends --no-install-suggests\
  build-essential \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade pip


WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 8080

CMD ["python3", "server.py"]