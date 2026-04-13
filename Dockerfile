# Utilise une image Python légère
FROM python:3.9-slim

# Définit le dossier de travail dans le conteneur
WORKDIR /app

# Installe les dépendances système nécessaires (si besoin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie le fichier requirements.txt et installe les bibliothèques
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le contenu de ton projet (api, dashboard, models, etc.)
COPY . .

# Expose le port utilisé par ton application (8001 dans ton code)
EXPOSE 8001

# Commande pour lancer l'API GhostBot
# On remplace 127.0.0.1 par 0.0.0.0 pour que Docker puisse communiquer avec l'extérieur
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]