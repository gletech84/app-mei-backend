FROM python:3.11-slim

WORKDIR /app

# evita problemas de build com dependências nativas
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# upgrade base tools
RUN pip install --upgrade pip setuptools wheel

# instalar dependências
COPY requirements.txt .
RUN pip install -r requirements.txt

# copiar código
COPY . .

# porta do Render
ENV PORT=10000

# start app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
