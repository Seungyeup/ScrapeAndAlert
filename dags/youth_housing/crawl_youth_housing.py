import logging
import requests
from datetime import datetime, timedelta

from airflow.providers.postgres.hooks.postgres import PostgresHook


def crawl_youth_housing(**context):
    """
    서울시 청년안심주택 공고를 크롤링하여,
    일주일 이내의 신규 공고만 Postgres에 저장하고 반환합니다.
    """
    url = (
        "https://soco.seoul.go.kr/youth/pgm/home/yohome/bbsListJson.json"
    )
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ko,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://soco.seoul.go.kr",
        "Referer": (
            "https://soco.seoul.go.kr/youth/bbs/BMSR00015/list.do?menuNo=400008"
        ),
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }
    data = {
        "bbsId": "BMSR00015",
        "pageIndex": "1",
        "searchAdresGu": "",
        "searchCondition": "",
        "searchKeyword": "",
    }

    try:
        # 1) API 호출
        resp = requests.post(url, headers=headers, data=data)
        resp.raise_for_status()
        raw = resp.json()

        # 2) 결과 구조 로깅
        logging.info("API returned JSON keys: %s", list(raw.keys()) if isinstance(raw, dict) else type(raw))
        # 3) resultList 추출
        if isinstance(raw, dict) and 'resultList' in raw:
            all_announcements = raw.get('resultList', [])
            # 페이징 정보도 로그에 남김
            paging = raw.get('pagingInfo', {})
            logging.info("Paging info: page %s/%s, total rows %s",
                         paging.get('pageIndex'), paging.get('totPage'), paging.get('totRow'))
        elif isinstance(raw, list):
            all_announcements = raw
        else:
            logging.error("Unexpected JSON structure: %s", raw)
            all_announcements = []

        logging.info("Fetched %d total announcements", len(all_announcements))
        logging.debug("Announcements data sample: %s", all_announcements[:3])

        # 4) 지난 일주일간 공고 필터링
        one_week_ago = datetime.now() - timedelta(days=7)
        recent = []
        for a in all_announcements:
            if not isinstance(a, dict):
                continue
            date_str = a.get('optn1', '')
            try:
                posted = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                logging.debug("Skipping invalid date format: %s", date_str)
                continue
            if posted >= one_week_ago:
                recent.append(a)

        logging.info("Filtered %d recent announcements", len(recent))

        # 5) DB에서 이미 보낸 공고 ID 조회
        pg = PostgresHook(postgres_conn_id='postgres_default')
        existing = pg.get_records("SELECT announcement_id FROM sent_announcements")
        sent_ids = {r[0] for r in existing}
        logging.info("Found %d already sent IDs in DB", len(sent_ids))

        # 6) 신규 공고 선별 및 저장
        new_items = []
        for a in recent:
            ann_id = a.get('boardId')
            if not ann_id or ann_id in sent_ids:
                continue
            item = {
                'id': ann_id,
                'title': a.get('nttSj', '').strip(),
                'date': a.get('optn1'),
                'url': (
                    'https://soco.seoul.go.kr'
                    f"/youth/pgm/home/yohome/bbsView.do?bbsNo={ann_id}&bbsId=BMSR00015"
                ),
            }
            new_items.append(item)

        logging.info("Identified %d new announcements to insert", len(new_items))

        if new_items:
            pg.insert_rows(
                table='sent_announcements',
                rows=[(it['id'],) for it in new_items],
                target_fields=['announcement_id'],
                commit_every=100,
            )
            logging.info("Recorded %d new announcements to DB", len(new_items))
        else:
            logging.info("No new announcements to insert.")

        # 7) XCom으로 신규 공고 리스트 반환
        return new_items

    except Exception as e:
        logging.exception("Error in crawl_youth_housing")
        return []
