FROM python:3.11-slim

LABEL authors="farukkamcici"

WORKDIR /api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app/
COPY startup_db.py startup_db.py

EXPOSE 8000

# Expect runtime envs to be provided by the platform (or --env-file):
# ENV, DEV_DB_PATH/PROD_DB_PATH, RELEASE_DB_URL, RELEASE_DB_SHA256
# On start: ensure DB exists, then serve.
CMD ["sh", "-c", "python -m startup_db && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
