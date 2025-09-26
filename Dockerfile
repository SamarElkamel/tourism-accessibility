FROM python:3.12-slim

WORKDIR /app

COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY etl/ ./etl
COPY dataviz/ ./dataviz

COPY scripts/run_etl.sh ./scripts/run_etl.sh
RUN chmod +x ./scripts/run_etl.sh

CMD ["./scripts/run_etl.sh"]
