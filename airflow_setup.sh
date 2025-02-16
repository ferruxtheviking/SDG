#!/bin/bash

# Run docker compose 
echo "Launching docker-compose"
docker compose up -d

sleep 60
# Create admin user
echo "Creating Admin user"
docker exec -d airflow airflow users create -e admin@example.org -f admin -l admin -r Admin -u admin -p admin

sleep 3
# Init the scheduler
echo "Starting scheduler"
docker exec -d airflow airflow scheduler