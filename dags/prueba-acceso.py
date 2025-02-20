import json
from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from functions import load_input_data, load_input_data_parameters, process_data, save_data_disk, save_data_mongo
from parameters import metadata, input

dag_args={
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=2)
}

dag = DAG(
    "prueba_acceso",
    default_args=dag_args,
    description="Prueba de acceso a SDG",
    schedule=timedelta(days=1),
    start_date=datetime(2021,1,1),
    catchup=False,
    tags=["test"],
    params={'metadata': metadata,
            'input': input}
)

def load_input_data_call(**kwargs):
    params = kwargs['dag_run'].conf
    if 'metadata' not in params:
        raise AirflowFailException("There's no metadata")
    return load_input_data(params.get('metadata'))

def load_input_data_call_2(**kwargs):
    params = kwargs['dag_run'].conf
    if 'metadata' not in params and 'input' not in params:
        raise AirflowFailException("There's no metadata or input")
    return load_input_data_parameters(params.get('input'))

def process_data_call(**kwargs):
    params = kwargs['dag_run'].conf
    input_data = kwargs['ti'].xcom_pull(task_ids='load_input_data')
    return process_data(params.get('metadata'), input_data)

def save_data_disk_call(**kwargs):
    params = kwargs['dag_run'].conf
    valid_data = kwargs['ti'].xcom_pull(task_ids='process_data')[0]
    invalid_data = kwargs['ti'].xcom_pull(task_ids='process_data')[1]
    return save_data_disk(valid_data, invalid_data, params.get('metadata'))

def save_data_mongo_call(**kwargs):
    valid_data = kwargs['ti'].xcom_pull(task_ids='process_data')[0]
    invalid_data = kwargs['ti'].xcom_pull(task_ids='process_data')[1]
    return save_data_mongo(valid_data, invalid_data)

load_input_data_task = PythonOperator(
    task_id="load_input_data",
    python_callable=load_input_data_call_2,
    provide_context=True,
    dag=dag
)

process_data_task = PythonOperator(
    task_id="process_data",
    python_callable=process_data_call,
    provide_context=True,
    dag=dag
)

save_data_disk_task = PythonOperator(
    task_id="save_data_disk",
    python_callable=save_data_disk_call,
    provide_context=True,
    dag=dag
)

save_data_mongo_task = PythonOperator(
    task_id="save_data_mongo",
    python_callable=save_data_mongo_call,
    provide_context=True,
    dag=dag
)
load_input_data_task >> process_data_task >> [ save_data_disk_task, save_data_mongo_task ]