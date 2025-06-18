#!/usr/bin/env python3

import os
import time
import signal
import sys
import logging
from logging.handlers import SysLogHandler
from datetime import datetime

# Configuration du logger
logger = logging.getLogger('classcord')
logger.setLevel(logging.INFO)

# Handler pour syslog
syslog_handler = SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_LOCAL0)
syslog_format = logging.Formatter('classcord: %(levelname)s - %(message)s')
syslog_handler.setFormatter(syslog_format)
logger.addHandler(syslog_handler)

# Handler pour la console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(console_format)
logger.addHandler(console)

# Configuration simple pour un serveur de démo
PORT = 12345

def signal_handler(sig, frame):
    logger.info("Signal reçu, arrêt propre du serveur...")
    sys.exit(0)

# Enregistrer le gestionnaire de signal
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    logger.info(f"Démarrage du serveur ClassCord sur le port {PORT}")
    
    try:
        # Log de démarrage du serveur
        logger.info("Serveur démarré avec succès")
        
        # Simuler des événements pour l'exemple
        while True:
            # Log des événements du serveur
            logger.debug("Vérification des connexions...")
            
            # Simulation d'une connexion (à remplacer par votre code réel)
            current_time = datetime.now().strftime("%H:%M:%S")
            if int(current_time.split(":")[2]) % 30 == 0:  # toutes les 30 secondes
                logger.info(f"Nouvel utilisateur connecté: user_{current_time}")
            
            # Simulation d'un message (à remplacer par votre code réel)
            if int(current_time.split(":")[2]) % 15 == 0:  # toutes les 15 secondes
                logger.info(f"Message reçu de user_{current_time}: 'Bonjour tout le monde!'")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interruption clavier reçue, arrêt du serveur...")
    except Exception as e:
        logger.error(f"Erreur critique: {str(e)}", exc_info=True)
    
    logger.info("Serveur arrêté")

if __name__ == "__main__":
    main()