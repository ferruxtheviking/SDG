# Base image
FROM apache/airflow:2.6.2

#  Create /data folder and give permissions to airflow user
USER root 
RUN mkdir -p /data && chown -R airflow:root /data

# Install the needed packages
USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
