#!/usr/bin/env python3
import os
import smtplib
from email.message import EmailMessage
import logging

def send_test_email():
    # 환경변수에서 설정 읽기
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))           # STARTTLS용 포트
    smtp_user = os.getenv('SMTP_USER')                       # 예: your@gmail.com
    smtp_password = os.getenv('SMTP_PASSWORD')               # 앱 비밀번호 16자리
    to_address = os.getenv('TO_EMAIL')                       # 테스트 수신 주소

    if not all([smtp_user, smtp_password, to_address]):
        raise RuntimeError("환경변수 SMTP_USER, SMTP_PASSWORD, TO_EMAIL 값을 모두 설정하세요.")

    # 이메일 메시지 구성
    msg = EmailMessage()
    msg['Subject'] = 'Airflow SMTP 테스트 메일'
    msg['From'] = smtp_user
    msg['To'] = to_address
    msg.set_content('이 메일은 SMTP 설정 확인을 위한 테스트 메일입니다.')

    logging.info(f"Connecting to SMTP server {smtp_host}:{smtp_port}…")
    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)
        logging.info("Test email sent successfully.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    try:
        send_test_email()
    except Exception as e:
        logging.error("Failed to send test email:", exc_info=e)
        exit(1)
