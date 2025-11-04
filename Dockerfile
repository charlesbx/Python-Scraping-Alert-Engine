# Image légère
FROM python:3.12-slim

# Env propres
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dépendances système (certifi/ssl/ca-certificates déjà incluses)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

# Dossier app
WORKDIR /app

# Installer deps Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier code
COPY monitor.py ./monitor.py
COPY src/ ./src/

# Créer dossiers (montés en volume ensuite)
RUN mkdir -p /app/data /app/logs

# Utilisateur non-root (bonnes pratiques)
RUN useradd -m app && chown -R app:app /app
USER app

# Par défaut, lance le script (on pourra override avec des args)
CMD ["python", "monitor.py"]
