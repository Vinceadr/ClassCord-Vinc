#!/bin/bash
# Script de démarrage manuel pour le serveur ClassCord
# Auteur: Vinceadr6
# Date: 2025-06-17 13:45:52

# Définition des variables
SERVER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="${SERVER_DIR}/classcord_server.log"
CONFIG_FILE="${SERVER_DIR}/config.json"

# Fonction pour afficher les messages
log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Vérification de l'existence du répertoire et du fichier serveur
if [ ! -f "${SERVER_DIR}/server_classcord.py" ]; then
  log_message "ERREUR: Fichier server_classcord.py introuvable dans $SERVER_DIR"
  exit 1
fi

# Vérification des dépendances
if ! command -v python3 &> /dev/null; then
  log_message "ERREUR: Python3 n'est pas installé. Installation..."
  apt-get update && apt-get install -y python3
fi

# Création du fichier de log s'il n'existe pas
touch "$LOG_FILE"

# Enregistrement du démarrage
log_message "DÉMARRAGE: Serveur ClassCord lancé par $(whoami)"

# Affichage des informations réseau
echo "=== Informations réseau ==="
ip_address=$(hostname -I | awk '{print $1}')
echo "Adresse IP: $ip_address"
echo "Port: 12345"
echo "=========================="

# Démarrage du serveur
log_message "INFO: Tentative de démarrage du serveur ClassCord..."
cd "$SERVER_DIR"
python3 server_classcord.py

# Cette partie sera exécutée uniquement si le serveur se termine
exit_code=$?
if [ $exit_code -ne 0 ]; then
  log_message "ERREUR: Le serveur s'est arrêté avec le code d'erreur $exit_code"
else
  log_message "INFO: Le serveur s'est arrêté normalement"
fi

exit $exit_code