FROM apache/airflow:2.9.3

# (필요 시) OS 패키지만 root로 설치
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# pip는 airflow 유저로 실행 + (권장) constraints 사용
USER airflow
ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
ARG CONSTRAINT_URL=https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt
RUN pip install --no-cache-dir --constraint "${CONSTRAINT_URL}" \
    joblib numpy pandas scikit-learn
