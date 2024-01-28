FROM python:3.10-slim-bullseye

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./worker.py /app/app.py

CMD [ "python3",  "app.py"]