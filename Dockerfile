FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir
COPY yatube/ .
CMD ["python3", "manage.py", "runserver", "0:8000"]

