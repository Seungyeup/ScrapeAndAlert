"""
청년안심주택 공고 크롤링 모듈
"""
import requests
import json
from datetime import datetime, timedelta
import os

def crawl_youth_housing():
    """
    서울시 청년안심주택 공고를 크롤링하는 함수
    """
    url = "https://soco.seoul.go.kr/youth/pgm/home/yohome/bbsListJson.json"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ko,en;q=0.9,ko-KR;q=0.8,en-US;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://soco.seoul.go.kr",
        "Referer": "https://soco.seoul.go.kr/youth/bbs/BMSR00015/list.do?menuNo=400008",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    data = {
        "bbsId": "BMSR00015",
        "pageIndex": "1",
        "searchAdresGu": "",
        "searchCondition": "",
        "searchKeyword": ""
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        print("응답 원문:", response.text)  # 응답 원문 출력
        result = response.json()
        all_announcements = result.get('resultList', [])
        
        # 지난 일주일간의 공고 필터링
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        recent_announcements = [
            a for a in all_announcements 
            if datetime.strptime(a.get('optn1', ''), "%Y-%m-%d") >= week_ago
        ]
        
        # 전체 공고를 파일로 저장
        data_dir = os.getenv('AIRFLOW_HOME', os.path.join(os.path.dirname(__file__), '../../data'))
        os.makedirs(data_dir, exist_ok=True)
        
        with open(os.path.join(data_dir, 'announcements.json'), 'w', encoding='utf-8') as f:
            json.dump(all_announcements, f, ensure_ascii=False, indent=2)
        
        return {
            'recent_announcements': recent_announcements
        }
        
    except Exception as e:
        print(f"Error during crawling: {str(e)}")
        return {
            'recent_announcements': []
        } 