import socket
import threading
import json
import time

# Configuration - À MODIFIER
HOST = '192.168.X.X'  # REMPLACE X.X par l'IP réelle de ton serveur
PORT = 12345

# Variables globales
client_socket = None
username = None
connected = False

def receive_messages():
    """Gère la réception des messages du serveur"""
    global client_socket, connected
    buffer = ""
    
    while True:
        try:
            # Reçoit les données
            data = client_socket.recv(1024)
            if not data:
                print("\nConnexion perdue avec le serveur")
                break
                
            # Ajoute les données au buffer
            buffer += data.decode('utf-8', errors='ignore')
            
            # Traite toutes les lignes complètes
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                
                # Essaie de parser le JSON
                try:
                    message = json.loads(line)
                    handle_message(message)
                except json.JSONDecodeError:
                    print(f"Message non-JSON reçu: {line}")
                
        except Exception as e:
            print(f"\nErreur de réception: {e}")
            break
    
    # Si on sort de la boucle, c'est que la connexion est perdue
    connected = False
    print("\nDéconnecté du serveur.")

def handle_message(message):
    """Traite un message JSON reçu du serveur"""
    global connected
    
    msg_type = message.get('type')
    
    if msg_type == 'error':
        print(f"\nErreur: {message.get('message')}")
        
    elif msg_type == 'register':
        if message.get('status') == 'ok':
            print("\nInscription réussie! Vous pouvez maintenant vous connecter.")
        
    elif msg_type == 'login':
        if message.get('status') == 'ok':
            connected = True
            print("\nConnexion réussie! Vous pouvez maintenant envoyer des messages.")
        
    elif msg_type == 'message':
        from_user = message.get('from', 'Anonyme')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '').split('T')[1].split('.')[0] if 'timestamp' in message else ''
        
        print(f"\n[{timestamp}] {from_user}: {content}")
        
    elif msg_type == 'status':
        user = message.get('user', 'Inconnu')
        state = message.get('state', 'inconnu')
        
        print(f"\n{user} est maintenant {state}")

def send_message(message_type, **kwargs):
    """Envoie un message au serveur au format JSON"""
    if not client_socket:
        print("Non connecté au serveur")
        return False
        
    message = {'type': message_type, **kwargs}
    try:
        client_socket.sendall((json.dumps(message) + '\n').encode('utf-8'))
        return True
    except Exception as e:
        print(f"Erreur d'envoi: {e}")
        return False

def register():
    """Gère l'inscription d'un nouvel utilisateur"""
    global username
    
    print("\n--- INSCRIPTION ---")
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")
    
    return send_message('register', username=username, password=password)

def login():
    """Gère la connexion d'un utilisateur"""
    global username
    
    print("\n--- CONNEXION ---")
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")
    
    return send_message('login', username=username, password=password)

def send_chat_message():
    """Envoie un message de chat"""
    if not connected:
        print("Vous devez être connecté pour envoyer un message")
        return False
        
    content = input("\nMessage: ")
    return send_message('message', content=content)

def set_status():
    """Change le statut de l'utilisateur"""
    if not connected:
        print("Vous devez être connecté pour changer votre statut")
        return False
        
    print("\n--- CHANGER DE STATUT ---")
    print("1. En ligne")
    print("2. Absent")
    print("3. Ne pas déranger")
    print("4. Invisible")
    
    choice = input("Choix: ")
    
    states = {
        '1': 'online',
        '2': 'away',
        '3': 'dnd',
        '4': 'invisible'
    }
    
    if choice in states:
        return send_message('status', state=states[choice])
    else:
        print("Choix invalide")
        return False

def main():
    global client_socket
    
    try:
        # Connexion au serveur
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connexion au serveur {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
        print("Connecté au serveur!")
        
        # Démarrer le thread de réception
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Menu principal
        while True:
            print("\n--- ClassCord CHAT ---")
            print("1. S'inscrire")
            print("2. Se connecter")
            print("3. Envoyer un message")
            print("4. Changer de statut")
            print("5. Quitter")
            
            choice = input("Choix: ")
            
            if choice == '1':
                register()
            elif choice == '2':
                login()
            elif choice == '3':
                send_chat_message()
            elif choice == '4':
                set_status()
            elif choice == '5':
                print("\nAu revoir!")
                break
            else:
                print("Choix invalide!")
                
    except ConnectionRefusedError:
        print("Connexion refusée. Vérifiez l'adresse IP et le port.")
    except KeyboardInterrupt:
        print("\nFermeture du client.")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        if client_socket:
            client_socket.close()

if __name__ == "__main__":
    main()