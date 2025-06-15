import pytest
from airflow.models import DagBag
from datetime import datetime, timedelta

def test_dag_loaded():
    """DAG가 제대로 로드되는지 테스트"""
    dag_bag = DagBag(dag_folder='dags/youth_housing', include_examples=False)
    assert len(dag_bag.import_errors) == 0, f"DAG 로드 중 에러 발생: {dag_bag.import_errors}"
    assert len(dag_bag.dags) > 0, "DAG가 없습니다."

def test_dag_structure():
    """DAG의 구조를 테스트"""
    dag_bag = DagBag(dag_folder='dags/youth_housing', include_examples=False)
    dag = dag_bag.get_dag(dag_id='youth_housing_monitor')
    
    assert dag is not None, "DAG를 찾을 수 없습니다."
    assert dag.schedule_interval == '0 9 * * *', "스케줄이 매일 오전 9시가 아닙니다."
    assert dag.start_date == datetime(2024, 3, 20), "시작 날짜가 2024-03-20이 아닙니다."
    assert not dag.catchup, "catchup이 False가 아닙니다."

def test_dag_tasks():
    """DAG의 태스크를 테스트"""
    dag_bag = DagBag(dag_folder='dags/youth_housing', include_examples=False)
    dag = dag_bag.get_dag(dag_id='youth_housing_monitor')
    
    tasks = dag.tasks
    task_ids = [task.task_id for task in tasks]
    
    assert len(tasks) == 2, "태스크 개수가 2개가 아닙니다."
    assert 'crawl_youth_housing' in task_ids, "crawl_youth_housing 태스크가 없습니다."
    assert 'send_email_notification' in task_ids, "send_email_notification 태스크가 없습니다."

def test_dag_task_dependencies():
    """DAG의 태스크 의존성을 테스트"""
    dag_bag = DagBag(dag_folder='dags/youth_housing', include_examples=False)
    dag = dag_bag.get_dag(dag_id='youth_housing_monitor')
    
    crawl_task = dag.get_task('crawl_youth_housing')
    notify_task = dag.get_task('send_email_notification')
    
    # crawl_task가 notify_task의 upstream인지 확인
    assert notify_task in crawl_task.downstream_list, "crawl_task가 notify_task의 upstream이 아닙니다."
    # notify_task가 crawl_task의 downstream인지 확인
    assert crawl_task in notify_task.upstream_list, "notify_task가 crawl_task의 downstream이 아닙니다." 