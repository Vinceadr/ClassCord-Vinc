# 📊 ClassCord Server - Documentation Technique

## 📝 Présentation du projet

ClassCord Server est un serveur de chat développé en Python qui permet à plusieurs clients de communiquer en temps réel via un protocole JSON sur socket TCP. Ce projet a été développé dans le cadre d'une semaine intensive du BTS SIO SISR, avec l'objectif de déployer et sécuriser un service réseau dans un environnement professionnel.

## 🔍 Architecture et technologies

### Technologies utilisées

- **Langage**: Python 3.10+
- **Communication**: Sockets TCP
- **Format d'échange**: JSON
- **Stockage**: Fichiers Pickle pour la persistance des données utilisateurs
- **Containerisation**: Docker et Docker Compose
- **Journalisation**: Module logging de Python
- **Monitoring**: Prometheus et Grafana pour la visualisation
- **Sécurisation**: Gestion des connexions avec authentification

### Architecture serveur

```
┌───────────────────────┐
│   ClassCord Server    │
├───────────────────────┤
│    Socket TCP (12345) │
├───────────────────────┤
│ JSON Message Protocol │
├──────────┬────────────┤
│ Users DB │ Logging    │
└──────────┴────────────┘
```

## 🚀 Fonctionnalités implémentées

### Gestion des utilisateurs

- ✅ Système d'inscription et d'authentification
- ✅ Persistance des données utilisateurs
- ✅ Suivi des connexions/déconnexions

### Communication

- ✅ Messagerie globale (broadcast)
- ✅ Messagerie privée (messages directs)
- ✅ Notification des changements de statut

### Journalisation et sécurité

- ✅ Logs détaillés des connexions et messages
- ✅ Gestion des erreurs et exceptions
- ✅ Synchronisation thread-safe (verrous)

### Déploiement et maintenance

- ✅ Containerisation avec Docker
- ✅ Configuration de docker-compose pour le monitoring
- ✅ Monitoring avec Prometheus/Grafana

## 📡 Protocole de communication

Le serveur utilise un protocole basé sur JSON pour communiquer avec les clients. Voici les principaux types de messages:

### Enregistrement d'un nouvel utilisateur

```json
{
  "type": "register",
  "username": "nom_utilisateur",
  "password": "mot_de_passe"
}
```

### Connexion

```json
{
  "type": "login",
  "username": "nom_utilisateur",
  "password": "mot_de_passe"
}
```

### Message global

```json
{
  "type": "message",
  "subtype": "global",
  "content": "Contenu du message"
}
```

### Message privé

```json
{
  "type": "message",
  "subtype": "private",
  "to": "destinataire",
  "content": "Contenu du message privé"
}
```

### Liste des utilisateurs

```json
{
  "type": "users"
}
```

## 🐳 Déploiement avec Docker

### Dockerfile

```Dockerfile
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
```

### Docker Compose

```yaml
version: "3"

services:
  classcord:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "12345:12345"
    restart: unless-stopped
    networks:
      - monitoring_network

  socket_exporter:
    build:
      context: ./prometheus
      dockerfile: Dockerfile.exporter
    ports:
      - "9091:9091"
    depends_on:
      - classcord
    networks:
      - monitoring_network

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    depends_on:
      - socket_exporter
    networks:
      - monitoring_network

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - monitoring_network

networks:
  monitoring_network:
```

### Installation et démarrage

1. Cloner le dépôt:

```bash
git clone https://github.com/votre-username/classcord-server.git
cd classcord-server
```

2. Lancer le serveur avec Docker Compose:

```bash
docker-compose up -d
```

3. Vérifier que les conteneurs sont bien démarrés:

```bash
docker-compose ps
```

### Monitoring avec Prometheus et Grafana

Le serveur ClassCord est configuré pour exposer des métriques via Prometheus, permettant de surveiller:

- Nombre de connexions actives
- Nombre de messages échangés
- Temps de réponse du serveur
- Utilisation des ressources système

Ces métriques sont visualisables via Grafana à l'adresse http://localhost:3000 (identifiant: admin, mot de passe: admin).

#### Configuration Prometheus

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "socket_bridge"
    static_configs:
      - targets: ["localhost:9091"]
    metrics_path: /metrics
```

## 📊 Structure du code

Le fichier principal `server_classcord.py` contient la logique du serveur:

```python
# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('classcord')

# Configuration
HOST = '0.0.0.0'
PORT = 12345

# Stockage des données
USER_FILE = 'users.pkl'
CLIENTS = {}  # socket: username
USERS = {}    # username: password
LOCK = threading.Lock()
```

Les fonctions principales:

- `load_users()`: Charge les utilisateurs depuis le fichier de persistance
- `save_users()`: Sauvegarde les utilisateurs dans le fichier
- `broadcast()`: Envoie un message à tous les clients connectés
- `handle_client()`: Gère la connexion avec un client
- `main()`: Démarre le serveur et accepte les connexions

## 📊 Exportation des données

Le serveur dispose d'un utilitaire permettant d'exporter les messages en format JSON ou CSV:

```python
#!/usr/bin/env python3
import sqlite3
import json
import csv
import sys
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path('../data/classcord.db')

def export_to_json(channel=None, output_file=None):
    """Exporte les messages en format JSON"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        channel_suffix = f"_{channel.replace('#', '')}" if channel else ""
        output_file = f"messages{channel_suffix}_{timestamp}.json"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if channel:
            cursor.execute(
                "SELECT username, channel, content, timestamp FROM messages WHERE channel = ? ORDER BY timestamp",
                (channel,)
            )
        else:
            cursor.execute(
                "SELECT username, channel, content, timestamp FROM messages ORDER BY channel, timestamp"
            )

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'username': row['username'],
                'channel': row['channel'],
                'content': row['content'],
                'timestamp': row['timestamp']
            })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

    print(f"Exportation JSON terminée: {len(messages)} messages exportés dans {output_file}")
    return output_file
```

## 🛡️ Monitoring avec Prometheus

Le serveur ClassCord est configuré avec un exportateur de métriques pour Prometheus:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
SOCKET_HOST = 'classcord'  # Nom du service Docker
SOCKET_PORT = 12345
HTTP_PORT = 9091
REFRESH_INTERVAL = 5  # Secondes

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            # Récupérer les métriques depuis le serveur socket
            try:
                metrics = self.fetch_metrics()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(metrics.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def fetch_metrics(self):
        """Récupère les métriques depuis le serveur socket"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SOCKET_HOST, SOCKET_PORT))
            s.sendall(b"GET_METRICS")

            # Réception des données
            chunks = []
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                chunks.append(chunk)

                # Si la réponse est complète, on peut sortir
                if len(chunk) < 1024:
                    break

            return b''.join(chunks).decode('utf-8')

def run_server():
    """Démarrer le serveur HTTP pour exposer les métriques à Prometheus"""
    server_address = ('', HTTP_PORT)
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"Starting metrics exporter on port {HTTP_PORT}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
```

## 📈 Tests et performance

Le serveur a été testé avec:

- Plusieurs connexions simultanées
- Communication stable sur réseau local
- Gestion efficace des déconnexions
- Persistance des données utilisateurs

## 🛡️ Sécurité

### Mesures implémentées

- Authentification par nom d'utilisateur et mot de passe
- Journalisation détaillée des connexions et messages
- Gestion des erreurs et exceptions
- Isolation des services via Docker
- Communication JSON sécurisée

## 📝 Journal de développement

### Jour 1

- Configuration de l'environnement de base
- Implémentation de la structure du serveur avec socket
- Test de connexions multiples

### Jour 2

- Système d'authentification
- Messagerie privée
- Configuration du logging

### Jour 3

- Mise en place de Docker
- Configuration de Prometheus
- Tests de performances

### Jour 4

- Configuration de Grafana
- Documentation du projet
- Exportation des données

### Jour 5

- Finalisation de la documentation
- Nettoyage du code
- Validation et tests finaux

## 👥 Contributeurs

- Vinceadr - Développeur principal
- Claude Sonnet 3.7 - Développeur secondaire
- Équipe pédagogique BTS SIO - Encadrement et conseil

---

_Ce projet a été réalisé dans le cadre d'une semaine intensive du BTS SIO SISR._
