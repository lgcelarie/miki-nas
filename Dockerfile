FROM python:3.10-slim-bullseye
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./main.py /app/
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]