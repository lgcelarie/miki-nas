from fastapi import FastAPI, Query
from typing import Annotated
import os
import pika
from pika.exchange_type import ExchangeType
app = FastAPI()

@app.get("/shutdown")
async def shutdown_host(q: Annotated[str | None, Query(max_length=50)] = None):
    if not q:
        return {"error":"token required"}
    elif q != os.getenv('CLIENT_TOKEN'):
        return {"error":"invalid token"}

    file_to_sync = 'file'
    with open(file_to_sync, "w") as f:
        f.write("shutdown")

@app.get("/media/sync")
def media_sync():
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('rabbitmq', credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange='plex', exchange_type=ExchangeType.direct)
    channel.queue_declare(queue='plex')
    channel.basic_publish(exchange='plex',
                          routing_key='plex',
                          body='sync')
    connection.close()
    return