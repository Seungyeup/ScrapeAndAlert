from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from youth_housing.crawl import crawl_youth_housing
from youth_housing.send_email import send_email
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_new_announcements(**context):
    crawl_result = context['task_instance'].xcom_pull(
        task_ids='crawl_youth_housing',
        key='return_value'
    )
    if not crawl_result or 'recent_announcements' not in crawl_result:
        return []
    recent_announcements = crawl_result['recent_announcements']
    return recent_announcements or []

with DAG(
    'youth_housing',
    default_args=default_args,
    description='청년안심주택 모니터링 DAG',
    schedule_interval='0 */6 * * *',  # 6시간마다 실행
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['youth_housing'],
) as dag:

    crawl_task = PythonOperator(
        task_id='crawl_youth_housing',
        python_callable=crawl_youth_housing,
    )

    check_task = PythonOperator(
        task_id='check_new_announcements',
        python_callable=check_new_announcements,
        retries=0,
    )

    send_email_task = PythonOperator(
        task_id='send_email',
        python_callable=send_email,
    )

    crawl_task >> check_task >> send_email_task
