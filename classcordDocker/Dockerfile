FROM python:3.9-slim

WORKDIR /app

# Copier le script start.sh avant les autres fichiers
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Gérer les requirements de façon conditionnelle
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else echo "No requirements.txt found"; fi

# Copier le reste des fichiers
COPY . .

# Utiliser tini pour une meilleure gestion des signaux
RUN apt-get update && apt-get install -y --no-install-recommends tini && apt-get clean

# Définir tini comme point d'entrée
ENTRYPOINT ["/usr/bin/tini", "--"]

# Utiliser notre script wrapper
CMD ["/app/start.sh"]