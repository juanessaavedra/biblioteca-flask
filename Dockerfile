# Dockerfile
FROM python:3.11-slim

# Instalar solo PostgreSQL client (lo mínimo necesario)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 5000

# Ejecutar aplicación
CMD ["python", "run.py"]