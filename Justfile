image := "mortgage_refinery_image"
container := "mortgage_refinery_container"
port := "8000"
envfile := ".env"

build:
    docker build -t {{image}}:latest .

run:
    docker run --name {{container}} {{image}}:latest

run-detached:
    docker run -d --name {{container}} -p {{port}}:{{port}} --env-file {{envfile}} {{image}}:latest

run-rm:
    docker run --rm {{image}}:latest

start:
    docker start {{container}}

stop:
    docker stop {{container}} || true

rm:
    docker rm -f {{container}} || true

logs:
    docker logs -f {{container}}

exec:
    docker exec -it {{container}} /bin/bash

rebuild:
    just rm && just build

clean:
    docker container prune -f
    docker image prune -f