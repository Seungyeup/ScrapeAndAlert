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
    
    # 공고 데이터 구조 검증
    if result['today_announcements']:
        announcement = result['today_announcements'][0]
        assert 'nttSj' in announcement  # 제목
        assert 'optn1' in announcement  # 공고일
        assert 'optn4' in announcement  # 모집기간
        assert 'content' in announcement  # 내용 