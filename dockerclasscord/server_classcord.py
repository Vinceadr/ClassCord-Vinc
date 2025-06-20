#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import json
import pickle
import os
import logging
from datetime import datetime

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

def load_users():
    """Charge les utilisateurs enregistrés depuis le fichier"""
    global USERS
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'rb') as f:
                USERS = pickle.load(f)
            logger.info(f"Utilisateurs chargés: {list(USERS.keys())}")
        except Exception as e:
            logger.error(f"Erreur de chargement des utilisateurs: {e}")
            USERS = {}
    else:
        logger.info("Aucun fichier d'utilisateurs trouvé, création d'une nouvelle base")
        USERS = {}

def save_users():
    """Sauvegarde les utilisateurs dans le fichier"""
    try:
        with open(USER_FILE, 'wb') as f:
            pickle.dump(USERS, f)
        logger.info("Utilisateurs sauvegardés")
    except Exception as e:
        logger.error(f"Erreur de sauvegarde des utilisateurs: {e}")

def broadcast(message, sender_socket=None):
    """Envoie un message à tous les clients connectés sauf celui spécifié"""
    for client_socket, username in list(CLIENTS.items()):
        if client_socket != sender_socket:
            try:
                client_socket.sendall((json.dumps(message) + '\n').encode())
                logger.debug(f"Broadcast à {username}: {message}")
            except Exception as e:
                logger.error(f"Erreur broadcast pour {username}: {e}")

def handle_client(client_socket):
    """Gère la connexion avec un client"""
    buffer = ''
    username = None
    address = client_socket.getpeername()
    logger.info(f"[CONNEXION] Nouvelle connexion depuis {address}")
    
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            
            buffer += data
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                logger.info(f"[RECU] {address} >> {line}")
                
                try:
                    msg = json.loads(line)
                    msg_type = msg.get('type', '').lower()
                    
                    if msg_type == 'register':
                        # Traitement de l'inscription
                        new_username = msg.get('username', '')
                        new_password = msg.get('password', '')
                        
                        with LOCK:
                            if new_username in USERS:
                                response = {'type': 'error', 'message': 'Username already exists.'}
                            else:
                                USERS[new_username] = new_password
                                save_users()
                                response = {'type': 'register', 'status': 'ok'}
                            
                            # Envoyer la réponse EXACTEMENT comme dans le code de référence
                            client_socket.sendall((json.dumps(response) + '\n').encode())
                            logger.info(f"[REGISTRE] Réponse envoyée: {response}")
                    
                    elif msg_type == 'login':
                        # Traitement de la connexion
                        login_username = msg.get('username', '')
                        login_password = msg.get('password', '')
                        
                        with LOCK:
                            if USERS.get(login_username) == login_password:
                                username = login_username
                                CLIENTS[client_socket] = username
                                response = {'type': 'login', 'status': 'ok', 'username': username}
                                client_socket.sendall((json.dumps(response) + '\n').encode())
                                
                                # Notifier les autres de la connexion
                                broadcast({'type': 'status', 'user': username, 'state': 'online'}, client_socket)
                                logger.info(f"[LOGIN] {username} connecté")
                            else:
                                response = {'type': 'error', 'message': 'Login failed.'}
                                client_socket.sendall((json.dumps(response) + '\n').encode())
                    
                    elif msg_type == 'message':
                        # Traitement des messages
                        if not username:
                            username = msg.get('from', 'invité')
                            with LOCK:
                                CLIENTS[client_socket] = username
                            logger.info(f"[INFO] Connexion invitée détectée : {username}")
                        
                        msg['from'] = username
                        msg['timestamp'] = datetime.now().isoformat()
                        
                        if msg.get('subtype') == 'private':
                            # Message privé
                            dest_user = msg.get('to')
                            target_socket = None
                            
                            with LOCK:
                                for sock, user in CLIENTS.items():
                                    if user == dest_user:
                                        target_socket = sock
                                        break
                            
                            if target_socket:
                                try:
                                    target_socket.sendall((json.dumps(msg) + '\n').encode())
                                    logger.info(f"[MP] {username} >> {dest_user} : {msg['content']}")
                                except Exception as e:
                                    logger.error(f"[ERREUR] envoi MP à {dest_user} : {e}")
                            else:
                                logger.info(f"[INFO] Utilisateur {dest_user} introuvable pour message privé")
                        else:
                            # Message global
                            logger.info(f"[MSG] {username} >> {msg['content']}")
                            broadcast(msg, client_socket)
                    
                    elif msg_type == 'status' and username:
                        # Changement de statut
                        broadcast({'type': 'status', 'user': username, 'state': msg['state']}, client_socket)
                        logger.info(f"[STATUS] {username} est maintenant {msg['state']}")
                    
                    elif msg_type == 'users' or msg_type == 'userlist':
                        # Liste des utilisateurs
                        with LOCK:
                            connected_users = list(CLIENTS.values())
                        response = {'type': 'users', 'users': connected_users}
                        client_socket.sendall((json.dumps(response) + '\n').encode())
                        logger.info(f"[INFO] Liste des utilisateurs envoyée à {username or address}: {connected_users}")
                
                except json.JSONDecodeError:
                    logger.warning(f"[WARN] Message non-JSON: {line}")
                except Exception as e:
                    logger.error(f"[ERREUR] Traitement: {e}")
    
    except Exception as e:
        logger.error(f'[ERREUR] Problème avec {address} ({username}): {e}')
    
    finally:
        # Nettoyage à la déconnexion
        if username:
            broadcast({'type': 'status', 'user': username, 'state': 'offline'}, client_socket)
        
        with LOCK:
            CLIENTS.pop(client_socket, None)
        
        try:
            client_socket.close()
        except:
            pass
        
        logger.info(f"[DECONNEXION] {address} déconnecté")

def start_server():
    """Démarre le serveur socket"""
    # Charger les utilisateurs
    load_users()
    
    # Créer et configurer le socket serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    logger.info(f"[DEMARRAGE] Serveur en écoute sur {HOST}:{PORT}")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
    
    except KeyboardInterrupt:
        logger.info("[ARRET] Arrêt du serveur")
    except Exception as e:
        logger.error(f"[ERREUR] Serveur: {e}")
    finally:
        server_socket.close()

if __name__ == '__main__':
    logger.info("[INIT] Initialisation du serveur ClassCord...")
    start_server()