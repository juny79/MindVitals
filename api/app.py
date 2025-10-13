from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import numpy as np

app = FastAPI(title="MindVitals API", version="0.1.0")

class BioSample(BaseModel):
    ts: str
    hr: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    spo2: Optional[float] = None
    temp_skin: Optional[float] = None
    steps: Optional[int] = None
    sleep_stage: Optional[str] = None

class IngestPayload(BaseModel):
    user_id: str
    samples: List[BioSample]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
def ingest(payload: IngestPayload):
    # TODO: persist to storage; for now, return basic stats
    n = len(payload.samples)
    hrs = [s.hr for s in payload.samples if s.hr is not None]
    return {
        "user_id": payload.user_id,
        "samples": n,
        "hr_avg": float(np.mean(hrs)) if hrs else None
    }

@app.post("/state-score")
def state_score(payload: IngestPayload):
    # Very simple demo score: higher HRV and steps increase score, high HR decreases
    hrv_vals = [s.hrv_rmssd for s in payload.samples if s.hrv_rmssd is not None]
    hr_vals = [s.hr for s in payload.samples if s.hr is not None]
    steps_vals = [s.steps for s in payload.samples if s.steps is not None]

    hrv = float(np.nanmean(hrv_vals)) if hrv_vals else 0.0
    hr = float(np.nanmean(hr_vals)) if hr_vals else 0.0
    steps = float(np.nanmean(steps_vals)) if steps_vals else 0.0

    score = 50.0 + (hrv * 0.2) + (steps * 0.001) - (hr * 0.1)
    score = max(0.0, min(100.0, score))
    return {"user_id": payload.user_id, "state_score": round(score, 2)}
