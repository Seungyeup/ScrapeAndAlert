import os
import socket
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

    # 0) SMTP 연결 디버깅 태스크
    def test_smtp_connection():
        host = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        port = int(os.getenv('SMTP_PORT', '587'))
        try:
            sock = socket.create_connection((host, port), timeout=10)
            sock.close()
            print(f"SMTP connection to {host}:{port} succeeded")
        except Exception as e:
            raise RuntimeError(f"SMTP connection to {host}:{port} failed: {e}")

    test_conn = PythonOperator(
        task_id='test_smtp_connection',
        python_callable=test_smtp_connection,
    )

    # 1) 크롤링 태스크
    crawl = PythonOperator(
        task_id='crawl_youth_housing',
        python_callable=crawl_youth_housing,
    )

    # 2) 이메일 알림 설정
    sender = os.getenv('YOUTH_HOUSING_SENDER_EMAIL')
    receivers = os.getenv('YOUTH_HOUSING_RECEIVER_EMAILS', '').split(',')

    notify = EmailOperator(
        task_id='send_email',
        to=receivers,
        subject='[역세권청년주택] 신규 모집공고 알림',
        html_content='{{ ti.xcom_pull(task_ids="crawl_youth_housing") }}',
        # smtp_conn_id='smtp_default',
    )

    # 태스크 순서: SMTP 연결 테스트 → 크롤링 → 이메일 전송
    test_conn >> crawl >> notify