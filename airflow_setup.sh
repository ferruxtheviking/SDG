#!/bin/bash

# Pull docker image
docker pull apache/airflow

# Run the the apache airflow service
docker run -d \
	--name airflow \
	-p 8090:8080 \
	-e LOAD_EX=y \
	-v "./dags:/opt/airflow/dags" \
	apache/airflow bash -c "airflow db init && airflow webserver"

sleep 5
# Create admin user
echo "Creating Admin user"
docker exec -d airflow airflow users create -e admin@example.org -f admin -l admin -r Admin -u admin -p admin

sleep 3
# Init the scheduler
echo "Starting scheduler"
docker exec -d airflow airflow scheduler
