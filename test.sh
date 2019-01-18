#!/bin/bash
export DEBUGMOUNT='.:/app/'
docker-compose down
docker-compose build
docker-compose up
echo 'honda-box stack down'
