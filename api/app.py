# api/app.py (기존 파일에 아래를 추가/교체)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import numpy as np, os, joblib
from pathlib import Path

app = FastAPI(title="MindVitals API", version="0.2.0")

class BioSample(BaseModel):
    ts: str
    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    temp_skin: Optional[float] = None
    steps: Optional[int] = None
    sleep_stage: Optional[str] = None
    sleep_hours: Optional[float] = None

class IngestPayload(BaseModel):
    user_id: str
    samples: List[BioSample]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
def ingest(payload: IngestPayload):
    n = len(payload.samples)
    hrs = [s.hr for s in payload.samples if s.hr is not None]
    return {"user_id": payload.user_id, "samples": n, "hr_avg": float(np.mean(hrs)) if hrs else None}

@app.post("/state-score")
def state_score(payload: IngestPayload):
    hrv_vals = [s.hrv_rmssd for s in payload.samples if s.hrv_rmssd is not None]
    hr_vals = [s.hr for s in payload.samples if s.hr is not None]
    steps_vals = [s.steps for s in payload.samples if s.steps is not None]
    sleep_vals = [s.sleep_hours for s in payload.samples if s.sleep_hours is not None]

    hrv = float(np.nanmean(hrv_vals)) if hrv_vals else 0.0
    hr = float(np.nanmean(hr_vals)) if hr_vals else 0.0
    steps = float(np.nanmean(steps_vals)) if steps_vals else 0.0
    sleep = float(np.nanmean(sleep_vals)) if sleep_vals else 0.0

    score = 50.0 + (hrv * 0.2) + (steps * 0.001) - (hr * 0.1) + (sleep * 3.0)
    score = max(0.0, min(100.0, score))
    return {"user_id": payload.user_id, "state_score": round(score, 2)}

MODEL_DIR = Path("./mlops/airflow_dags/models")
RULE = MODEL_DIR / "state_score_rule.pkl"

def _rule_score(hr, hrv, steps, sleep):
    # rule 파일 없으면 기본값
    coefs = {"bias": 50.0, "hrv_rmssd": 0.2, "hr": -0.1, "steps": 0.001, "sleep_hours": 3.0}
    if RULE.exists():
        coefs = joblib.load(RULE)
    score = (
        coefs["bias"] +
        coefs["hrv_rmssd"] * (hrv or 0.0) +
        coefs["hr"] * (hr or 0.0) +
        coefs["steps"] * (steps or 0.0) +
        coefs["sleep_hours"] * (sleep or 0.0)
    )
    return float(max(0.0, min(100.0, score)))

@app.post("/predict/state")
def predict_state(payload: IngestPayload):
    # 최근 샘플 평균으로 간단 추론
    hrv = np.nanmean([s.hrv_rmssd for s in payload.samples if s.hrv_rmssd is not None]) if payload.samples else 0.0
    hr = np.nanmean([s.hr for s in payload.samples if s.hr is not None]) if payload.samples else 0.0
    steps = np.nanmean([s.steps for s in payload.samples if s.steps is not None]) if payload.samples else 0.0
    sleep = np.nanmean([s.sleep_hours for s in payload.samples if s.sleep_hours is not None]) if payload.samples else 0.0
    score = round(_rule_score(hr, hrv, steps, sleep), 2)

    # 간단 권고(룰)
    recs = []
    if score < 60:
        recs = ["3분 박스호흡", "10분 집중명상", "취침 90분 전 스크린타임 차단"]
    elif score < 75:
        recs = ["5분 박스호흡", "산책 10분"]
    else:
        recs = ["저강도 스트레칭 5분", "수분 섭취"]

    return {"user_id": payload.user_id, "state_score": score, "recommendations": recs}

@app.post("/recommend")
def recommend(payload: IngestPayload):
    # 컨텍스트 없이 간단 추천 샘플
    return {"user_id": payload.user_id, "topN": ["3분 박스호흡", "7분 바디스캔", "산책 10분"]}
