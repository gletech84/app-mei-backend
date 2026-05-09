FROM python:3.11-slim

WORKDIR /app

# Evita problemas de cache/pip
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Atualiza pip
RUN pip install --upgrade pip

# Copia requirements
COPY backend/requirements.txt /app/requirements.txt

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia projeto inteiro
COPY . /app

# Expõe porta do Render
ENV PORT=10000

# Start da aplicação
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
