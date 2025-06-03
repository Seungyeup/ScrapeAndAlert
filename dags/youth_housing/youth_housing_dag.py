from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from youth_housing.crawl import crawl_youth_housing
from youth_housing.send_email import send_email


def check_new_announcements(**context):
    # 크롤링 결과 가져오기
    crawl_result = context['task_instance'].xcom_pull(task_ids='crawl_youth_housing')
    
    # 오늘 날짜의 공고 목록
    today_announcements = crawl_result['today_announcements']
    
    # 새로운 공고가 있으면 알림 발송
    if today_announcements:
        return today_announcements
    return []

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'youth_housing',
    default_args=default_args,
    description='청년안심주택 모니터링 DAG',
    schedule_interval='0 */6 * * *',  # 6시간마다 실행
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['youth_housing'],
) as dag:

    crawl_task = PythonOperator(
        task_id='crawl_youth_housing',
        python_callable=crawl_youth_housing,
    )

    check_task = PythonOperator(
        task_id='check_new_announcements',
        python_callable=check_new_announcements,
    )

    send_email_task = PythonOperator(
        task_id='send_email',
        python_callable=send_email,
    )

    crawl_task >> check_task >> send_email_task 