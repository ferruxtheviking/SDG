#!/bin/bash

# Get env variables
source .env

# Run docker compose 
echo "Launching docker-compose"
docker compose up -d

# Create admin user
echo "Creating Admin user"
docker exec -d airflow airflow users create -e admin@example.org -f admin -l admin -r Admin -u $ADMIN_USER -p $ADMIN_PASSWORD

# Init the scheduler
echo "Starting scheduler"
docker exec -d airflow airflow scheduler