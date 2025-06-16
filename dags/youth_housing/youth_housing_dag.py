# dags/youth_housing/youth_housing_dag.py
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
from youth_housing.crawl_youth_housing import crawl_youth_housing

# 기본 DAG 인자 설정
default_args = {
    'owner': 'airflow',                           # DAG 소유자
    'depends_on_past': False,                     # 이전 태스크 상태와 독립적으로 실행
    'start_date': datetime(2025, 6, 1),           # 시작일
    'retries': 1,                                 # 실패 시 재시도 횟수
    'retry_delay': timedelta(minutes=5),          # 재시도 간격
}

with DAG(
    dag_id='youth_housing',
    schedule_interval='0 6 * * *',                # 매일 오전 6시에 실행
    default_args=default_args,
    catchup=False,                                # 백필 동작 비활성화
) as dag:

    # 1) 크롤링 태스크
    crawl = PythonOperator(
        task_id='crawl_youth_housing',
        python_callable=crawl_youth_housing,
    )

    # 2) 이메일 알림 설정
    # 환경변수로부터 발신자, 수신자 정보 가져오기
    sender = os.getenv('YOUTH_HOUSING_SENDER_EMAIL')
    receivers = os.getenv('YOUTH_HOUSING_RECEIVER_EMAILS', '').split(',')

    notify = EmailOperator(
        task_id='send_email',
        to=receivers,
        from_email=sender,                         
        subject='[역세권청년주택] 신규 모집공고 알림',
        html_content='{{ ti.xcom_pull(task_ids="crawl_youth_housing") }}',
        # smtp_conn_id: Connection으로 SMTP 설정 시 사용
        # smtp_conn_id='smtp_default',
    )

    crawl >> notify
