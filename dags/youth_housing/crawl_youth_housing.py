# dags/youth_housing/crawl_youth_housing.py
import json
from airflow.providers.postgres.hooks.postgres import PostgresHook

def crawl_youth_housing(**context):
    # (기존) 크롤링 로직으로 all_announcements 리스트 확보
    all_announcements = [...]  # 각 요소에 'id', 'title', 'url' 등 포함

    pg = PostgresHook(postgres_conn_id='postgres_default') # 기본 연결 ID
    existing = pg.get_records("SELECT announcement_id FROM sent_announcements")
    sent_ids = {row[0] for row in existing}

    # 신규 공고만 필터
    new_announcements = [
        ann for ann in all_announcements
        if ann['id'] not in sent_ids
    ]

    # DB에 INSERT (신규 공고만)
    if new_announcements:
        insert_sql = """
        INSERT INTO sent_announcements (announcement_id)
        VALUES (%s)
        ON CONFLICT DO NOTHING
        """
        pg.insert_rows(
            table='sent_announcements',
            rows=[(ann['id'],) for ann in new_announcements],
            target_fields=['announcement_id'],
            commit_every=100
        )

    # XCom 에 신규 공고 리스트 전달
    return new_announcements
