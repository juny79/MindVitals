import streamlit as st
import requests, json

st.set_page_config(page_title="MindVitals Dashboard", layout="wide")
st.title("🧘‍♀️ MindVitals — Dashboard (Local MVP)")

col1, col2 = st.columns(2)
with col1:
    st.subheader("상태 점수 예측")
    hr = st.number_input("HR", 40, 200, 72)
    hrv = st.number_input("HRV (RMSSD)", 0, 200, 34)
    steps = st.number_input("Steps", 0, 40000, 5000)
    sleep = st.number_input("Sleep Hours", 0.0, 12.0, 6.5, step=0.5)
    if st.button("Predict"):
        payload = {"user_id":"demo","samples":[{"ts":"now","hr":hr,"hrv_rmssd":hrv,"steps":steps,"sleep_hours":sleep}]}
        r = requests.post("http://api:8000/predict/state", json=payload)  # docker 네트워크 내 서비스명
        st.json(r.json())

with col2:
    st.subheader("추천 루틴")
    if st.button("Get Recommendations"):
        payload = {"user_id":"demo","samples":[{"ts":"now"}]}
        r = requests.post("http://api:8000/recommend", json=payload)
        st.json(r.json())
