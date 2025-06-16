"""
dags/youth_housing/crawl_youth_housing.py

서울시 청년안심주택 공고를 크롤링하여,
신규 공고만 Postgres에 기록하고 XCom으로 반환합니다.
"""
import logging
import requests
import json
from datetime import datetime, timedelta

from airflow.providers.postgres.hooks.postgres import PostgresHook


def crawl_youth_housing(**context):
    # 1) API 호출 설정
    url = "https://soco.seoul.go.kr/youth/pgm/home/yohome/bbsListJson.json"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ko,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://soco.seoul.go.kr",
        "Referer": "https://soco.seoul.go.kr/youth/bbs/BMSR00015/list.do?menuNo=400008",
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/136.0.0.0 Safari/537.36"),
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
        # 2) 크롤링
        resp = requests.post(url, headers=headers, data=data)
        resp.raise_for_status()
        result = resp.json()
        all_announcements = result.get("resultList", [])

        # 3) 지난 일주일간 공고만 필터
        one_week_ago = datetime.now() - timedelta(days=7)
        recent = []
        for a in all_announcements:
            dt_str = a.get("optn1", "")
            try:
                posted = datetime.strptime(dt_str, "%Y-%m-%d")
            except Exception:
                continue
            if posted >= one_week_ago:
                recent.append(a)

        # 4) DB에서 이미 보낸 공고 ID 조회
        pg = PostgresHook(postgres_conn_id="postgres_default")
        rows = pg.get_records("SELECT announcement_id FROM sent_announcements")
        sent_ids = {r[0] for r in rows}

        # 5) 신규 공고만 선별 & DB에 INSERT
        new_announcements = []
        for a in recent:
            ann_id    = a.get("bbsNo")
            ann_title = a.get("bbsSj", "").strip()
            ann_date  = a.get("optn1")
            ann_url   = (
                "https://soco.seoul.go.kr"
                f"/youth/pgm/home/yohome/bbsView.do?bbsNo={ann_id}&bbsId=BMSR00015"
            )
            if ann_id and ann_id not in sent_ids:
                new_announcements.append({
                    "id":    ann_id,
                    "title": ann_title,
                    "date":  ann_date,
                    "url":   ann_url,
                })

        if new_announcements:
            pg.insert_rows(
                table="sent_announcements",
                rows=[(ann["id"],) for ann in new_announcements],
                target_fields=["announcement_id"],
                commit_every=100,
            )
            logging.info("DB에 %d개의 신규 공고 ID를 기록했습니다.", len(new_announcements))
        else:
            logging.info("신규 공고가 없습니다.")

        # 6) XCom으로 신규 공고 리스트 반환
        return new_announcements

    except Exception as e:
        logging.error("crawl_youth_housing 실패: %s", str(e))
        # 재시도 로직이 있다면 빈 리스트 반환
        return []
