# mlops/airflow_dags/weekly_train_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path
import pandas as pd
import numpy as np
import joblib, os

FEATURE_DIR = Path("/opt/airflow/dags/local_features")
MODEL_DIR = Path("/opt/airflow/dags/models")
MODEL_DIR.mkdir(exist_ok=True)

def train_state_score(**context):
    # 가장 최근 feature 파일 로드
    files = sorted(FEATURE_DIR.glob("feat_*.csv"))
    if not files:
        raise RuntimeError("No features found. Run daily_etl first.")
    df = pd.read_csv(files[-1])
    # 간단 회귀 대용: 규칙 기반 점수 → 모델처럼 저장
    # score = 50 + 0.2*hrv - 0.1*hr + 0.001*steps + 3*sleep_hours
    coefs = {"bias": 50.0, "hrv_rmssd": 0.2, "hr": -0.1, "steps": 0.001, "sleep_hours": 3.0}
    joblib.dump(coefs, MODEL_DIR / "state_score_rule.pkl")

with DAG(
    dag_id="weekly_train",
    start_date=datetime(2025,10,1),
    schedule_interval="0 3 * * 1",  # 매주 월요일 03:00
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["train","mindvitals"]
):
    PythonOperator(task_id="train_state_score", python_callable=train_state_score)
