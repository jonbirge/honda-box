#!/bin/bash
COMPOSE_FILE=docker-compose-debug.yml
docker-compose -f $COMPOSE_FILE down
docker-compose -f $COMPOSE_FILE build
docker-compose -f $COMPOSE_FILE up
docker-compose -f $COMPOSE_FILE down
rm -rf __pycache__
