# 🚀 ClassCord Server - Guide de déploiement complet

Ce document présente un guide pas à pas pour déployer le serveur ClassCord, un service de tchat multi-clients développé en Python. Il est conçu pour permettre à n'importe qui de reprendre le projet et de le mettre en place sans difficulté, même sans connaissances préalables du projet.

## 📋 Table des matières

1. [Présentation du projet](#présentation-du-projet)
2. [Prérequis systèmes](#prérequis-systèmes)
3. [Architecture technique](#architecture-technique)
4. [Guide d'installation étape par étape](#guide-dinstallation-étape-par-étape)
5. [Configuration du serveur](#configuration-du-serveur)
6. [Mise en place de la sécurité](#mise-en-place-de-la-sécurité)
7. [Déploiement avec Docker](#déploiement-avec-docker)
8. [Configuration du monitoring](#configuration-du-monitoring)
9. [Sauvegarde et maintenance](#sauvegarde-et-maintenance)
10. [Dépannage](#dépannage)
11. [Documentation pour les utilisateurs SLAM](#documentation-pour-les-utilisateurs-slam)

## 📝 Présentation du projet

ClassCord Server est un serveur de tchat qui permet à plusieurs clients de communiquer en temps réel via un protocole JSON sur socket TCP. Il a été développé dans le cadre d'une semaine intensive du BTS SIO SISR. Le serveur gère :

- L'authentification des utilisateurs
- L'envoi de messages (globaux et privés)
- Le suivi des statuts des utilisateurs (en ligne, hors ligne, etc.)
- La persistance des données utilisateurs

## 💻 Prérequis systèmes

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- Système d'exploitation Linux (Ubuntu 22.04/Debian 12 recommandés)
- Python 3.10+ (`python3 --version` pour vérifier)
- Git (`git --version`)
- Docker et docker-compose (optionnel mais recommandé)
- Un pare-feu comme UFW (`sudo apt install ufw`)

## 🏗 Architecture technique

Le serveur ClassCord est organisé selon l'architecture suivante :

```
.
├── server_classcord.py      # Fichier principal du serveur
├── users.pkl                # Stockage des utilisateurs (créé automatiquement)
├── Dockerfile               # Configuration Docker pour le serveur
├── docker-compose.yml       # Configuration pour tous les services
├── prometheus/              # Dossier contenant les configurations Prometheus
│   ├── Dockerfile.exporter  # Configuration du collecteur de métriques
│   ├── prometheus.yml       # Configuration Prometheus
│   └── socket_exporter.py   # Script d'exportation de métriques
├── export_messages.py       # Utilitaire d'exportation des messages
└── README.md                # Ce guide
```

## 🚀 Guide d'installation étape par étape

### 1. Clonage du dépôt Git

```bash
# Créer un dossier pour le projet
mkdir -p ~/projects
cd ~/projects

# Cloner le dépôt GitHub
git clone https://github.com/AstrowareConception/classcord-server.git
cd classcord-server
```

### 2. Installation des dépendances

```bash
# Installer les packages nécessaires
sudo apt update
sudo apt install -y python3 python3-pip ufw

# Installer les modules Python requis
pip3 install -r requirements.txt
```

Si le fichier `requirements.txt` n'existe pas, créez-le avec le contenu suivant :

```
# requirements.txt
sqlite3
```

### 3. Configuration du pare-feu

```bash
# Autoriser les connexions sur le port du serveur
sudo ufw allow 12345/tcp

# Activer le pare-feu s'il ne l'est pas déjà
sudo ufw enable

# Vérifier l'état du pare-feu
sudo ufw status
```

### 4. Création d'un utilisateur dédié

```bash
# Créer un utilisateur 'classcord' pour exécuter le serveur
sudo useradd -m classcord
sudo passwd classcord

# Donner les permissions sur le dossier du projet
sudo cp -r ~/projects/classcord-server /home/classcord/
sudo chown -R classcord:classcord /home/classcord/classcord-server
```

## ⚙️ Configuration du serveur

### 1. Configuration manuelle (sans Docker)

#### a. Créer un service systemd

```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/classcord.service
```

Contenu à ajouter au fichier :

```ini
[Unit]
Description=Serveur ClassCord
After=network.target

[Service]
User=classcord
WorkingDirectory=/home/classcord/classcord-server
ExecStart=/usr/bin/python3 /home/classcord/classcord-server/server_classcord.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Activer et démarrer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable classcord.service
sudo systemctl start classcord.service

# Vérifier l'état du service
sudo systemctl status classcord.service
```

#### b. Vérifier le fonctionnement du serveur

```bash
# Vérifier que le serveur écoute bien sur le port 12345
ss -tulpn | grep 12345

# Consulter les logs du service
sudo journalctl -u classcord -f
```

## 🔒 Mise en place de la sécurité

### 1. Installation de fail2ban

```bash
# Installer fail2ban
sudo apt install -y fail2ban

# Copier le fichier de configuration par défaut
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Éditer le fichier de configuration
sudo nano /etc/fail2ban/jail.local
```

Ajoutez cette configuration à la fin du fichier :

```ini
[classcord]
enabled = true
port = 12345
filter = classcord
logpath = /var/log/classcord.log
maxretry = 5
bantime = 3600
```

Créez un filtre fail2ban :

```bash
sudo nano /etc/fail2ban/filter.d/classcord.conf
```

Contenu du fichier :

```ini
[Definition]
failregex = \[ERREUR\] Problème avec <HOST>.*
ignoreregex =
```

Redémarrez fail2ban :

```bash
sudo systemctl restart fail2ban
```

### 2. Mise en place de la journalisation

Modifiez le script Python pour qu'il écrive dans un fichier log :

```bash
sudo nano /home/classcord/classcord-server/server_classcord.py
```

Ajoutez en début de fichier, après les autres imports :

```python
import logging
logging.basicConfig(
    filename='/var/log/classcord.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('classcord')
```

Remplacez les appels à `print()` par `logger.info()` ou `logger.error()`.

Assurez-vous que le fichier log est accessible :

```bash
sudo touch /var/log/classcord.log
sudo chown classcord:classcord /var/log/classcord.log
```

### 3. Configurer logrotate

```bash
sudo nano /etc/logrotate.d/classcord
```

Contenu du fichier :

```
/var/log/classcord.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 classcord classcord
    postrotate
        systemctl restart classcord
    endscript
}
```

## 🐳 Déploiement avec Docker

### 1. Création des fichiers Docker

#### a. Dockerfile pour le serveur

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

#### b. Configuration de l'exportateur de métriques

Créez un dossier pour Prometheus et son exportateur :

```bash
mkdir -p prometheus
cd prometheus
```

Créez le fichier Dockerfile.exporter :

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY socket_exporter.py /app/

RUN chmod +x /app/socket_exporter.py

EXPOSE 9091

CMD ["python", "/app/socket_exporter.py"]
```

Créez le fichier socket_exporter.py :

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

#### c. Configuration Prometheus

Créez le fichier prometheus.yml :

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "socket_bridge"
    static_configs:
      - targets: ["socket_exporter:9091"]
    metrics_path: /metrics
```

#### d. Fichier docker-compose.yml

Revenez au répertoire principal et créez le fichier docker-compose.yml :

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
    volumes:
      - ./data:/app/data

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

### 2. Lancement des conteneurs

```bash
# Assurez-vous d'être dans le répertoire du projet
cd ~/projects/classcord-server

# Créer le dossier pour les données persistantes
mkdir -p data

# Construire et lancer les conteneurs
docker-compose up -d

# Vérifier que les conteneurs sont actifs
docker-compose ps
```

## 📊 Configuration du monitoring

### 1. Accès à Prometheus

Une fois les conteneurs lancés, vous pouvez accéder à Prometheus via votre navigateur :

- URL : http://votre-ip:9090

### 2. Configuration de Grafana

1. Accédez à Grafana via votre navigateur :

   - URL : http://votre-ip:3000
   - Identifiant : admin
   - Mot de passe : admin (changez-le lors de la première connexion)

2. Ajoutez une source de données Prometheus :

   - Dans le menu latéral, allez dans "Configuration" > "Data sources"
   - Cliquez sur "Add data source"
   - Sélectionnez "Prometheus"
   - URL : http://prometheus:9090
   - Cliquez sur "Save & Test"

3. Importez un tableau de bord :
   - Dans le menu latéral, allez dans "+" > "Import"
   - Téléchargez un tableau de bord depuis Grafana.com ou créez le vôtre

## 💾 Sauvegarde et maintenance

### 1. Sauvegarde automatique des données

Créez un script de sauvegarde :

```bash
nano backup_classcord.sh
```

Contenu du script :

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/classcord/backups"

# Créer le dossier de sauvegarde s'il n'existe pas
mkdir -p $BACKUP_DIR

# Sauvegarder le fichier des utilisateurs
if [ -f /home/classcord/classcord-server/users.pkl ]; then
    cp /home/classcord/classcord-server/users.pkl $BACKUP_DIR/users_$TIMESTAMP.pkl
    echo "Sauvegarde du fichier utilisateurs effectuée : users_$TIMESTAMP.pkl"
fi

# Si vous utilisez SQLite, ajoutez la sauvegarde de la base
if [ -f /home/classcord/classcord-server/data/classcord.db ]; then
    cp /home/classcord/classcord-server/data/classcord.db $BACKUP_DIR/classcord_$TIMESTAMP.db
    echo "Sauvegarde de la base de données effectuée : classcord_$TIMESTAMP.db"
fi

# Nettoyer les anciennes sauvegardes (garder les 7 dernières)
find $BACKUP_DIR -name "users_*.pkl" -type f -mtime +7 -delete
find $BACKUP_DIR -name "classcord_*.db" -type f -mtime +7 -delete
```

Rendez le script exécutable :

```bash
chmod +x backup_classcord.sh
```

Ajoutez une tâche cron pour l'exécuter automatiquement :

```bash
sudo crontab -e
```

Ajoutez cette ligne pour une sauvegarde quotidienne à 2h du matin :

```
0 2 * * * /home/classcord/classcord-server/backup_classcord.sh
```

### 2. Mise à jour du serveur

Pour mettre à jour le serveur à partir du dépôt git :

```bash
cd ~/projects/classcord-server
git pull origin main

# Si vous utilisez Docker
docker-compose down
docker-compose build
docker-compose up -d

# Si vous utilisez systemd
sudo systemctl restart classcord
```

## 🔧 Dépannage

### Problèmes courants et solutions

1. **Le serveur ne démarre pas**

   - Vérifiez les logs : `sudo journalctl -u classcord -f`
   - Assurez-vous que Python est installé : `python3 --version`
   - Vérifiez les permissions : `ls -la /home/classcord/classcord-server/`

2. **Les clients ne peuvent pas se connecter**

   - Vérifiez que le port est ouvert : `sudo ufw status`
   - Vérifiez que le serveur écoute bien : `ss -tulpn | grep 12345`
   - Si vous êtes derrière un NAT, assurez-vous que le port est correctement redirigé

3. **Problèmes avec Docker**
   - Vérifiez l'état des conteneurs : `docker-compose ps`
   - Consultez les logs : `docker-compose logs -f`

## 📱 Documentation pour les utilisateurs SLAM

### Protocole de connexion

Pour se connecter au serveur ClassCord, les clients doivent :

1. Se connecter à l'adresse IP du serveur sur le port 12345
2. Utiliser le protocole JSON pour l'authentification et les messages
3. Envoyer des messages formatés selon le format décrit ci-dessous

### Format des messages

#### Enregistrement d'un nouvel utilisateur

```json
{
  "type": "register",
  "username": "nom_utilisateur",
  "password": "mot_de_passe"
}
```

#### Connexion

```json
{
  "type": "login",
  "username": "nom_utilisateur",
  "password": "mot_de_passe"
}
```

#### Message global

```json
{
  "type": "message",
  "subtype": "global",
  "content": "Contenu du message"
}
```

#### Message privé

```json
{
  "type": "message",
  "subtype": "private",
  "to": "destinataire",
  "content": "Contenu du message privé"
}
```

#### Demande de liste des utilisateurs

```json
{
  "type": "users"
}
```

### Exemple de connexion avec Telnet (pour tests)

```bash
# Se connecter au serveur avec Telnet
telnet ip-du-serveur 12345

# Envoyer un message au format JSON (entrez la ligne suivante puis appuyez sur Entrée)
{"type":"message","subtype":"global","from":"invité","content":"Bonjour tout le monde !"}
```

## 🏆 Conclusion

Ce guide complet vous permettra de déployer le serveur ClassCord dans différentes configurations, de le sécuriser et de le maintenir. Si vous rencontrez des problèmes ou avez des questions, n'hésitez pas à consulter la documentation ou à contacter l'équipe de développement.

---

**Projet développé par Vinceadr dans le cadre du BTS SIO SISR 2024.**
