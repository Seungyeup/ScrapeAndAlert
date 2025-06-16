"""
이메일 전송 모듈
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime
import logging

def send_email():
    """
    크롤링 결과를 이메일로 전송하는 함수
    """
    # 환경 변수에서 이메일 설정 가져오기
    sender_email = os.environ.get('YOUTH_HOUSING_SENDER_EMAIL')
    sender_password = os.environ.get('YOUTH_HOUSING_SENDER_PASSWORD')
    receiver_emails = os.environ.get('YOUTH_HOUSING_RECEIVER_EMAILS', '').split(',')
    
    if not all([sender_email, sender_password, receiver_emails]):
        logging.error("이메일 설정이 완료되지 않았습니다.")
        return
    
    # 크롤링 결과 읽기
    data_dir = '/tmp/youth_housing'
    try:
        with open(os.path.join(data_dir, 'announcements.json'), 'r', encoding='utf-8') as f:
            announcements = json.load(f)
    except Exception as e:
        logging.error("결과 파일 읽기 실패: %s", str(e))
        return

    # 이미 이메일을 보낸 공고 추적 파일
    sent_announcements_file = os.path.join(data_dir, 'sent_announcements.json')
    try:
        with open(sent_announcements_file, 'r', encoding='utf-8') as f:
            sent_announcements = json.load(f)
    except FileNotFoundError:
        sent_announcements = []

    # 새로운 공고만 필터링
    new_announcements = [
        a for a in announcements 
        if a['title'] not in [sa['title'] for sa in sent_announcements]
    ]

    if not new_announcements:
        logging.info("새로운 공고가 없습니다.")
        return

    # 이메일 내용 작성
    msg = MIMEMultipart()
    msg['Subject'] = '청년안심주택 공고 알림'
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_emails)
    
    # HTML 형식의 이메일 본문
    html = """
    <html>
        <body>
            <h2>청년안심주택 새로운 공고 알림</h2>
            <p>최근 등록된 청년안심주택 공고 목록입니다:</p>
            <ul>
    """
    
    for announcement in new_announcements:
        html += f"""
            <li>
                <strong>{announcement['title']}</strong><br>
                등록일: {announcement['optn1']}<br>
                <a href="https://soco.seoul.go.kr/youth/bbs/BMSR00015/view.do?menuNo=400008&bbsId=BMSR00015&nttId={announcement['nttId']}">자세히 보기</a>
            </li>
        """
    
    html += """
            </ul>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    try:
        # Gmail SMTP 서버 연결
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # 이메일 전송
        server.send_message(msg)
        server.quit()
        
        # 전송한 공고 기록 업데이트
        sent_announcements.extend(new_announcements)
        with open(sent_announcements_file, 'w', encoding='utf-8') as f:
            json.dump(sent_announcements, f, ensure_ascii=False, indent=2)
            
        logging.info("이메일 전송 완료")
        
    except Exception as e:
        logging.error("이메일 전송 실패: %s", str(e)) 