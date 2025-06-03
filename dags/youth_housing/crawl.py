"""
청년안심주택 공고 크롤링 모듈
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def crawl_youth_housing():
    """
    청년안심주택 공고를 크롤링하는 함수
    """
    url = "https://www.myhome.go.kr/hws/portal/cont/selectContRentalView.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        announcements = []
        
        # 여기에 실제 크롤링 로직 구현
        # 예시:
        for item in soup.select('.rental-list li'):
            title = item.select_one('.title').text.strip()
            date = item.select_one('.date').text.strip()
            announcements.append({
                'title': title,
                'date': date
            })
        
        # 결과를 파일로 저장
        data_dir = '/opt/airflow/data'
        os.makedirs(data_dir, exist_ok=True)
        
        with open(f'{data_dir}/announcements.json', 'w', encoding='utf-8') as f:
            json.dump(announcements, f, ensure_ascii=False, indent=2)
            
        return announcements
        
    except Exception as e:
        print(f"Error during crawling: {str(e)}")
        return [] 