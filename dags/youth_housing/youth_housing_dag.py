# dags/youth_housing/youth_housing_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from youth_housing.crawl_youth_housing import crawl_youth_housing
from youth_housing.send_email import send_email_task

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='youth_housing',
    schedule_interval='0 6 * * *',
    default_args=default_args,
    catchup=False,
) as dag:

    crawl = PythonOperator(
        task_id='crawl_youth_housing',
        python_callable=crawl_youth_housing,
        provide_context=True,
    )

    notify = PythonOperator(
        task_id='send_email',
        python_callable=send_email_task,
        provide_context=True,
    )

    crawl >> notify
