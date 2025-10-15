# mlops/airflow_dags/daily_etl_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os, json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("/opt/airflow/dags/local_data")
FEATURE_DIR = Path("/opt/airflow/dags/local_features")
DATA_DIR.mkdir(exist_ok=True)
FEATURE_DIR.mkdir(exist_ok=True)

def generate_dummy_data(**context):
    # 일자별 간단 더미 데이터 (HR/HRV/steps)
    ts = datetime.utcnow().isoformat()
    df = pd.DataFrame([{
        "ts": ts, "hr": 70, "hrv_rmssd": 35, "steps": 5000, "sleep_hours": 6.5
    }])
    out = DATA_DIR / f"raw_{datetime.utcnow().date()}.csv"
    df.to_csv(out, index=False)

def preprocess(**context):
    today = f"raw_{datetime.utcnow().date()}.csv"
    src = DATA_DIR / today
    df = pd.read_csv(src)
    # 간단 전처리: 유효범위 필터
    df = df[(df["hr"] > 20) & (df["hr"] < 220)]
    df.to_csv(DATA_DIR / f"clean_{datetime.utcnow().date()}.csv", index=False)

def feature_engineering(**context):
    clean = DATA_DIR / f"clean_{datetime.utcnow().date()}.csv"
    df = pd.read_csv(clean)
    # 아주 기본 피처: ANS balance-like
    df["ans_balance"] = (df["hrv_rmssd"] * 0.2) - (df["hr"] * 0.1)
    df.to_csv(FEATURE_DIR / f"feat_{datetime.utcnow().date()}.csv", index=False)

with DAG(
    dag_id="daily_etl",
    start_date=datetime(2025,10,1),
    schedule_interval="0 2 * * *",  # 매일 02:00
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["etl","mindvitals"]
):
    t1 = PythonOperator(task_id="generate_dummy_data", python_callable=generate_dummy_data)
    t2 = PythonOperator(task_id="preprocess", python_callable=preprocess)
    t3 = PythonOperator(task_id="feature_engineering", python_callable=feature_engineering)
    t1 >> t2 >> t3
