FROM python:3.11-slim

WORKDIR /app

COPY req.txt .
RUN pip install -r req.txt

COPY . .

CMD ["uvicorn", "src.app:APP", "--host", "0.0.0.0", "--port", "8000"]