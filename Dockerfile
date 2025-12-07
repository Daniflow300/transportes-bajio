FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

