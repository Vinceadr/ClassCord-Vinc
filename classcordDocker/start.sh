#!/bin/bash
# Script pour gérer les signaux et démarrer l'application ClassCord

# Fonction pour gérer les interruptions proprement
function handle_sigterm() {
  echo "Reçu SIGTERM, arrêt propre..."
  kill -TERM "$child" 2>/dev/null
  wait "$child"
  exit 0
}

# Enregistrer le gestionnaire pour SIGTERM
trap handle_sigterm SIGTERM SIGINT

# Démarrer l'application
echo "Démarrage de ClassCord..."
python server_classcord.py &
child=$!

# Attendre que le processus se termine
wait "$child"
exit $?