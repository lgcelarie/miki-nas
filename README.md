# Homeserver services

This is just a repository for a few services that i implement on my Homeserver. To be precise, to help me with:

- shutting it down without ssh into it: Using a /shutdown GET endpoint with a token, i just have to access it to initiate the shutdown procedure (the host is running a cronjob for the file sync).
- Moving my torrents to a folder accesible by Plex: using /media/sync i trigger the moving process. But taking into account that the process may take too long and reach a timeout, I implemented a messaging queue for a worker to actually handle the blocking process. I know there are many other (possibly more efficient) methods, but just wanted to use a queue as communication method between services.

## Getting this up and running
First of all, build the images from the root and the `worker` folder. After that, you can use the orchestration tool of choice. At the moment, i will use docker compose, but possibly include a helm repo, just to use Kubernetes hehe.

Here's an example of the contents of the `docker-compose.yaml`:
```
services:

worker:

image: miki-worker

depends_on:

rabbitmq:

condition: service_healthy

restart: true

environment:

- PLEX_TOKEN=your-plex-token
- PLEX_HOST="host:port of your instance"

volumes:

- "/your-media-origin/test:/origin"

- "/your-media-destination:/destination"

api:

image: miki-api

environment:

- CLIENT_TOKEN=value

ports:

- 18080:80

volumes:

- "/folder-with-shutdown-sync-file/file:/app/file"

rabbitmq:

image: rabbitmq:3-management-alpine

container_name: 'rabbitmq'

ports:

- 5672:5672

- 15672:15672

healthcheck:

test: rabbitmq-diagnostics -q ping

interval: 30s

timeout: 30s

retries: 10
```

## Support
There is none. I mean, this is not really meant for production environments.