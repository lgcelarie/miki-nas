import pika, sys, os, subprocess
import shutil
import functools
import logging
import requests
from pathlib import Path
from pika.exchange_type import ExchangeType

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def on_message(chan, method_frame, header_frame, body, userdata=None):
    src_folder='/origin'
    subfolders = ['series','movies']
    dst_folder='/destination'
    plex_host = os.getenv('PLEX_HOST')
    """Called when a message is received. Log message and ack it."""
    LOGGER.info('Delivery properties: %s, message metadata: %s', method_frame, header_frame)
    LOGGER.info('Userdata: %s, message body: %s', userdata, body)
    if body.decode() == 'sync':
            LOGGER.info('Recieved sync message. Processing...')
            for subfolder in subfolders:
                move_files( Path(src_folder).joinpath(subfolder), Path(dst_folder).joinpath(subfolder))
            LOGGER.info('Moving process completed.')
            LOGGER.info('Sending plex the request to sync library')
            params = {'X-Plex-Token': os.getenv('PLEX_TOKEN')}
            try:
                response = requests.get(f'http://{plex_host}/library/sections/29/refresh', params=params)
                LOGGER.info('Request to plex server sent... mission complete!')
            except requests.exceptions.ConnectionError:
                LOGGER.error('A connection error ocurred')
            except requests.exceptions.HTTPError:
                LOGGER.error(f'a {response.status_code} was returned')
    else:
        LOGGER.warning('unknown message received')
    chan.basic_ack(delivery_tag=method_frame.delivery_tag)

def move_files(source, destination):
    if not os.path.exists(source):
        LOGGER.error(f"Source directory '{source}' does not exist.")
        return

    if not os.path.exists(destination):
        os.makedirs(destination)

    # Iterate through all items in the source directory
    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)

        # If it's a directory, recursively copy it
        if os.path.isdir(source_path):
            move_files(source_path, destination_path)
        else:
            # If it's a file, copy it
            shutil.move(source_path, destination_path)
            LOGGER.info(f"Moved '{item}' to '{destination}'")

def main():
    """Main method."""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('rabbitmq', credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(
        exchange='plex',
        exchange_type=ExchangeType.direct,
        passive=False,
        auto_delete=False)
    channel.queue_declare(queue='plex')
    channel.queue_bind(
        queue='plex', exchange='plex', routing_key='plex')
    channel.basic_qos(prefetch_count=1)

    on_message_callback = functools.partial(
        on_message, userdata='on_message_userdata')
    channel.basic_consume('plex', on_message_callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    main()
