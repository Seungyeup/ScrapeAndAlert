import pytest
from datetime import datetime
from dags.youth_housing.crawl import crawl_youth_housing

def test_crawl_youth_housing():
    # 크롤링 실행
    result = crawl_youth_housing()
    
    # 결과 검증
    assert isinstance(result, dict)
    assert 'today_announcements' in result
    assert isinstance(result['today_announcements'], list)
    
    # 오늘 날짜의 공고만 있는지 확인
    today = datetime.now().strftime("%Y-%m-%d")
    for announcement in result['today_announcements']:
        assert announcement['optn1'] == today 