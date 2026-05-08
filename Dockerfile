FROM python:3.11-slim

WORKDIR /app

# evita bugs de build
RUN pip install --upgrade pip setuptools wheel

# dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# código
COPY . .

ENV PORT=10000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
