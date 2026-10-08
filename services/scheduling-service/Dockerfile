# Build from the repository root: docker build -f services/scheduling-service/Dockerfile .
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY libs/python/smartedu_contracts /opt/libs/smartedu_contracts
COPY libs/python/smartedu_infra /opt/libs/smartedu_infra
COPY libs/python/smartedu_observability /opt/libs/smartedu_observability
COPY libs/python/smartedu_perf /opt/libs/smartedu_perf
COPY libs/python/smartedu_security /opt/libs/smartedu_security
COPY services/scheduling-service/requirements.txt ./requirements.txt
COPY requirements.constraints.txt ./constraints.txt
RUN pip install -c constraints.txt --timeout 120 --retries 5 --prefer-binary --no-cache-dir -r requirements.txt /opt/libs/smartedu_contracts /opt/libs/smartedu_infra /opt/libs/smartedu_observability /opt/libs/smartedu_perf /opt/libs/smartedu_security \
    && useradd --create-home --uid 10001 appuser
COPY --chown=10001:10001 services/scheduling-service/app ./app
COPY --chown=10001:10001 services/scheduling-service/migrations ./migrations
COPY --chown=10001:10001 services/scheduling-service/alembic.ini ./alembic.ini
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=15s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
