# dags/youth_housing/send_email.py
from airflow.operators.email import EmailOperator

def send_email_task(**context):
    new_list = context['ti'].xcom_pull(task_ids='crawl_youth_housing')
    if not new_list:
        return  # 보낼 신규 공고가 없으면 종료

    body = "\n\n".join(
        f"{ann['title']} — {ann['url']}" for ann in new_list
    )

    email = EmailOperator(
        task_id='send_email',
        to="{{ var.value.YOUTH_HOUSING_RECEIVER_EMAILS }}".split(','),
        subject="새로운 청년주택 공고 알림",
        html_content=body,
    )
    return email.execute(context=context)
