import pytest
import os
from dags.youth_housing.notify import send_email_notification

def test_send_email_notification():
    
    sender_email = os.getenv('YOUTH_HOUSING_SENDER_EMAIL')
    sender_password = os.getenv('YOUTH_HOUSING_SENDER_PASSWORD')
    receiver_emails = os.getenv('YOUTH_HOUSING_RECEIVER_EMAILS', '').split(',')
    
    # 환경 변수가 없으면 테스트 스킵
    if not all([sender_email, sender_password]) or not receiver_emails:
        pytest.skip("이메일 설정이 없습니다. 환경변수를 확인해주세요.")
    
    # 테스트용 더미 데이터
    test_announcements = [
        {
            "nttSj": "테스트 공고",
            "optn1": "2024-03-20",
            "optn4": "2024-03-25",
            "content": "■주택위치 : 서울시 강남구 ■공급호수 : 10세대"
        }
    ]
    
    # 이메일 발송 테스트
    try:
        send_email_notification(test_announcements)
        assert True
    except Exception as e:
        pytest.fail(f"이메일 발송 실패: {str(e)}") 