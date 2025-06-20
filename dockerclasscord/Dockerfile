FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier du serveur
COPY server_classcord.py /app/

# S'assurer que le script est exécutable
RUN chmod +x /app/server_classcord.py

# Exposer le port socket
EXPOSE 12345

# Commande de démarrage
CMD ["python", "/app/server_classcord.py"]