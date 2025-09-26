FROM python:3.12-slim

RUN pip install --no-cache-dir mysql-connector-python requests

WORKDIR /app

COPY etl/ ./etl
COPY dataviz/ ./dataviz

COPY scripts/run_etl.sh ./scripts/run_etl.sh
RUN chmod +x ./scripts/run_etl.sh

CMD ["./scripts/run_etl.sh"]
