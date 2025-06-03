import json
import os
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def send_email_notification(announcements):
    # 환경 변수 로드
    load_dotenv()
    
    # 이메일 설정
    sender_email = os.getenv('YOUTH_HOUSING_SENDER_EMAIL')
    sender_password = os.getenv('YOUTH_HOUSING_SENDER_PASSWORD')
    receiver_emails = os.getenv('YOUTH_HOUSING_RECEIVER_EMAILS', '').split(',')
    
    if not all([sender_email, sender_password]) or not receiver_emails:
        raise ValueError("이메일 설정이 없습니다. 환경 변수를 확인해주세요.")
    
    # 이메일 메시지 생성
    msg = MIMEMultipart()
    msg['Subject'] = f'청년안심주택 공고 알림 ({datetime.now().strftime("%Y-%m-%d")})'
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_emails)
    
    # HTML 내용 생성
    html_content = """
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .announcement { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }
                .title { font-size: 18px; font-weight: bold; color: #333; }
                .info { margin: 5px 0; color: #666; }
            </style>
        </head>
        <body>
            <h2>새로운 청년안심주택 공고가 있습니다</h2>
    """
    
    for announcement in announcements:
        html_content += f"""
            <div class="announcement">
                <div class="title">{announcement['nttSj']}</div>
                <div class="info">공고일: {announcement['optn1']}</div>
                <div class="info">접수기간: {announcement['optn4']}</div>
                <div class="info">{announcement['content']}</div>
            </div>
        """
    
    html_content += """
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # SMTP 서버 연결 및 이메일 발송
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
    except Exception as e:
        print(f"이메일 발송 중 오류 발생: {str(e)}")
        raise 