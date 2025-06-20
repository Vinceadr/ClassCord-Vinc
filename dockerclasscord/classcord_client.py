#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import time
import sys
import os
import argparse

class ClassCordTestClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.authenticated = False
        self.username = None
        self.receive_thread = None
        self.running = True
        self.users_online = set()  # Pour suivre les utilisateurs en ligne
        
    def connect(self, host, port):
        """Établit la connexion au serveur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            print(f"\n[*] Connecté au serveur {host}:{port}")
            
            # Démarrer le thread de réception
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"\n[!] Erreur de connexion: {e}")
            return False
    
    def authenticate(self, username, password=None):
        """S'authentifier auprès du serveur"""
        if not self.connected:
            print("\n[!] Non connecté au serveur")
            return False
        
        try:
            self.username = username
            
            if password:
                auth_message = f"LOGIN:{username}:{password}"
            else:
                auth_message = f"LOGIN:{username}:guest"
            
            print(f"\n[*] Tentative d'authentification en tant que {username}...")
            self.socket.send(auth_message.encode('utf-8'))
            
            # L'authentification sera confirmée par le thread de réception
            time.sleep(1)  # Attendre un peu pour donner le temps au serveur de répondre
            
            return True
        except Exception as e:
            print(f"\n[!] Erreur d'authentification: {e}")
            return False
    
    def send_message(self, message):
        """Envoie un message au serveur"""
        if not self.connected:
            print("\n[!] Non connecté au serveur")
            return False
        
        try:
            if message.startswith("/"):
                # Commandes spéciales
                if message == "/quit" or message == "/exit":
                    self.socket.send("LOGOUT".encode('utf-8'))
                    print("\n[*] Déconnexion...")
                    self.running = False
                    return True
                elif message == "/users":
                    print("\n--- Utilisateurs en ligne ---")
                    for user in self.users_online:
                        print(f"- {user}")
                    print("---------------------------")
                    return True
                else:
                    print(f"\n[!] Commande inconnue: {message}")
                    return False
            else:
                # Message normal
                full_message = f"MSG:{self.username}:{message}"
                self.socket.send(full_message.encode('utf-8'))
                return True
        except Exception as e:
            print(f"\n[!] Erreur d'envoi: {e}")
            self.connected = False
            return False
    
    def receive_messages(self):
        """Réception des messages du serveur"""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    print("\n[!] Connexion fermée par le serveur")
                    self.connected = False
                    break
                
                # Ajouter les données au buffer
                buffer += data.decode('utf-8', errors='replace')
                
                # Traiter les messages complets (terminés par \n ou non)
                messages = buffer.split('\n')
                buffer = messages.pop()  # Garder le dernier fragment incomplet
                
                for message in messages:
                    message = message.strip()
                    if not message:
                        continue
                        
                    self.process_message(message)
                    
                # Traiter le reste si c'est un message complet
                if buffer and (':' in buffer or buffer.startswith("AUTH") or buffer.startswith("LOGIN")):
                    self.process_message(buffer)
                    buffer = ""
                    
            except Exception as e:
                if self.running:
                    print(f"\n[!] Erreur de réception: {e}")
                    self.connected = False
                break
    
    def process_message(self, message):
        """Traite un message reçu du serveur"""
        # Messages d'authentification
        if "AUTH_OK" in message or "LOGIN_SUCCESS" in message or "CONNECTED" in message or message == "AUTHENTICATED":
            self.authenticated = True
            print(f"\n[*] Authentification réussie en tant que {self.username}")
            return
        
        # Messages système (connexion/déconnexion d'utilisateurs)
        if "SYSTEM:" in message or "s'est connecté" in message or "s'est déconnecté" in message:
            print(f"\n[SYSTÈME] {message.split(':', 1)[1] if ':' in message else message}")
            
            # Mise à jour de la liste des utilisateurs
            user_match = None
            if "s'est connecté" in message:
                user_match = message.split("s'est connecté")[0].strip()
                if ":" in user_match:
                    user_match = user_match.split(":", 1)[1].strip()
                self.users_online.add(user_match)
                
            elif "s'est déconnecté" in message:
                user_match = message.split("s'est déconnecté")[0].strip()
                if ":" in user_match:
                    user_match = user_match.split(":", 1)[1].strip()
                if user_match in self.users_online:
                    self.users_online.remove(user_match)
            
            return
        
        # Messages normaux
        if ":" in message and not message.startswith("MSG_") and not message.startswith("ERROR:"):
            parts = message.split(":", 1)
            username = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else ""
            
            # Si c'est un message de type MESSAGE:username:content
            if username == "MESSAGE" and ":" in content:
                msg_parts = content.split(":", 1)
                username = msg_parts[0].strip()
                content = msg_parts[1].strip() if len(msg_parts) > 1 else ""
            
            # Ajouter l'utilisateur à la liste des connectés s'il n'y est pas
            if username != "SYSTEM" and username != self.username:
                self.users_online.add(username)
            
            # Afficher le message s'il n'est pas vide
            if content:
                print(f"\n[{username}] {content}")
            
            return
        
        # Autres messages
        if not (message.startswith("MSG_OK") or message.startswith("NEED_AUTH") or message.startswith("WELCOME")):
            print(f"\n[Serveur] {message}")
    
    def disconnect(self):
        """Se déconnecter proprement"""
        self.running = False
        if self.connected:
            try:
                self.socket.send("LOGOUT".encode('utf-8'))
                time.sleep(0.5)  # Laisser le temps au serveur de traiter
                self.socket.close()
            except:
                pass
        self.connected = False

def clear_screen():
    """Effacer l'écran selon le système d'exploitation"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_help():
    """Affiche l'aide des commandes disponibles"""
    print("\n--- Commandes disponibles ---")
    print("/users - Afficher les utilisateurs en ligne")
    print("/quit ou /exit - Se déconnecter et quitter")
    print("---------------------------")

def main():
    parser = argparse.ArgumentParser(description='ClassCord Test Client')
    parser.add_argument('-s', '--server', default='localhost', help='Adresse du serveur (défaut: localhost)')
    parser.add_argument('-p', '--port', type=int, default=12345, help='Port du serveur (défaut: 12345)')
    args = parser.parse_args()
    
    clear_screen()
    print("========================================")
    print("        ClassCord Test Client")
    print("========================================")
    
    client = ClassCordTestClient()
    
    # Connexion au serveur
    if not client.connect(args.server, args.port):
        print("[!] Impossible de se connecter au serveur. Vérifiez l'adresse et le port.")
        sys.exit(1)
    
    # Menu de connexion
    print("\nComment voulez-vous vous connecter?")
    print("1. Compte avec mot de passe")
    print("2. Mode invité")
    
    choice = input("Votre choix (1/2): ")
    
    if choice == "1":
        username = input("Nom d'utilisateur: ")
        password = input("Mot de passe: ")
        client.authenticate(username, password)
    else:
        username = input("Pseudo invité (laissez vide pour 'Invité'): ") or "Invité"
        client.authenticate(username)
    
    print("\n[*] Appuyez sur Entrée pour envoyer un message")
    print("[*] Utilisez /help pour afficher les commandes disponibles")
    
    try:
        while client.running and client.connected:
            message = input("> ")
            
            if not message:
                continue
                
            if message == "/help":
                display_help()
                continue
                
            client.send_message(message)
    except KeyboardInterrupt:
        print("\n[*] Programme interrompu par l'utilisateur")
    finally:
        client.disconnect()
        print("[*] Déconnecté")

if __name__ == "__main__":
    main()