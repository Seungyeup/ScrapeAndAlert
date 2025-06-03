import requests
import json
from datetime import datetime

def crawl_youth_housing():
    # API 엔드포인트
    url = "https://soco.seoul.go.kr/youth/pgm/home/yohome/bbsListJson.json"
    
    # 요청 헤더
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ko,en;q=0.9,ko-KR;q=0.8,en-US;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://soco.seoul.go.kr',
        'Referer': 'https://soco.seoul.go.kr/youth/bbs/BMSR00015/list.do?menuNo=400008',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 요청 파라미터
    data = {
        "bbsId": "BMSR00015",
        "pageIndex": 1,
        "searchAdresGu": "",
        "searchCondition": "",
        "searchKeyword": ""
    }
    
    try:
        # API 요청
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        # JSON 응답 파싱
        data = response.json()
        
        # 응답 구조 검증
        if 'resultList' not in data:
            raise ValueError(f"Unexpected API response structure: {data}")
        
        # 오늘 날짜의 공고만 필터링
        today = datetime.now().strftime("%Y-%m-%d")
        today_announcements = [
            item for item in data['resultList']
            if item.get('optn1') == today  # optn1은 공고일
        ]
            
        return {
            'today_announcements': today_announcements,
            'raw_data': data  # 디버깅을 위해 원본 데이터도 포함
        }
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 실패: {str(e)}")
        print(f"요청 URL: {url}")
        print(f"요청 데이터: {data}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 실패: {str(e)}")
        print(f"응답 내용: {response.text}")
        raise
    except Exception as e:
        print(f"예상치 못한 에러 발생: {str(e)}")
        raise 