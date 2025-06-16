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
        resp = requests.post(url, headers=headers, data=data)
        resp.raise_for_status()

        all_announcements = resp.json()  # JSON 배열

        one_week_ago = datetime.now() - timedelta(days=7)
        recent = []
        for a in all_announcements:
            date_str = a.get("optn1", "")
            try:
                posted = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                continue
            if posted >= one_week_ago:
                recent.append(a)

        # Postgres 연결
        pg = PostgresHook(postgres_conn_id="postgres_default")
        existing = pg.get_records(
            "SELECT announcement_id FROM sent_announcements"
        )
        sent_ids = {r[0] for r in existing}

        new_items = []
        for a in recent:
            ann_id = a.get("boardId")
            if ann_id in sent_ids or ann_id is None:
                continue
            item = {
                "id": ann_id,
                "title": a.get("nttSj", "").strip(),
                "date": a.get("optn1"),
                "url": (
                    "https://soco.seoul.go.kr"
                    f"/youth/pgm/home/yohome/bbsView.do?bbsNo={ann_id}&bbsId=BMSR00015"
                ),
            }
            new_items.append(item)

        if new_items:
            pg.insert_rows(
                table="sent_announcements",
                rows=[(it["id"],) for it in new_items],
                target_fields=["announcement_id"],
                commit_every=100,
            )
            logging.info("Recorded %d new announcements to DB", len(new_items))
        else:
            logging.info("No new announcements found.")

        return new_items

    except Exception as e:
        logging.error("Error in crawl_youth_housing: %s", e)
        return []
