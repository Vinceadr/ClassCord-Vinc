# Documentation de connexion au serveur ClassCord

## Informations de connexion

- **IP d'accès** : 10.0.108.xx (IP de l'hôte physique)
- **Port** : 12345
- **Date de mise en service** : 2025-06-17

## Architecture réseau

```
╭───────────────╮         ╭──────────────────────────╮
│  Client Java  │         │    Serveur ClassCord     │
│               │ ◀─────▶│    (10.0.108.xx:12345)   │
│  Utilisateur  │         │                          │
╰───────────────╯         ╰──────────────────────────╯
                                    │
                                    ▼
                          ╭──────────────────────────╮
                          │      Base de données     │
                          │      des messages        │
                          ╰──────────────────────────╯
```

L'architecture utilise un modèle client-serveur où:

- Les clients Java se connectent au serveur via l'adresse IP 10.0.108.xx sur le port 12345
- Le serveur traite les demandes d'authentification et de messagerie
- Les messages sont stockés dans une base de données persistante
- La communication utilise des sockets TCP pour une fiabilité maximale

## Extrait de log de connexion réussi

```
[2025-06-17 12:44:55] INFO: Serveur ClassCord démarré sur 0.0.0.0:12345
[2025-06-17 12:45:10] INFO: Nouvelle connexion établie depuis 10.0.112.23
[2025-06-17 12:45:15] INFO: Utilisateur 'Vinceadr5' authentifié avec succès
[2025-06-17 12:45:20] INFO: Message reçu de Vinceadr5: "Bonjour, test de connexion"
[2025-06-17 12:45:25] INFO: Message distribué aux 3 utilisateurs connectés
```

## Exemple d'utilisation du client Java

```java
import java.io.*;
import java.net.*;

/**
 * Client Java pour la connexion au serveur ClassCord
 */
public class ClassCordClient {
    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;
    private final String serverIp;
    private final int serverPort;
    private String username;

    /**
     * Constructeur du client ClassCord
     * @param serverIp L'adresse IP du serveur
     * @param serverPort Le port du serveur
     */
    public ClassCordClient(String serverIp, int serverPort) {
        this.serverIp = serverIp;
        this.serverPort = serverPort;
    }

    /**
     * Établit une connexion avec le serveur
     * @return true si la connexion est établie avec succès, false sinon
     */
    public boolean connect() {
        try {
            socket = new Socket(serverIp, serverPort);
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            System.out.println("Connexion établie avec le serveur " + serverIp + ":" + serverPort);
            return true;
        } catch (IOException e) {
            System.err.println("Erreur de connexion : " + e.getMessage());
            return false;
        }
    }

    /**
     * Authentifie l'utilisateur auprès du serveur
     * @param username Nom d'utilisateur
     * @param password Mot de passe
     * @return true si l'authentification est réussie, false sinon
     */
    public boolean login(String username, String password) {
        try {
            this.username = username;
            out.println("LOGIN:" + username + ":" + password);
            String response = in.readLine();
            System.out.println("Réponse du serveur : " + response);
            return response.startsWith("SUCCESS");
        } catch (IOException e) {
            System.err.println("Erreur lors de l'authentification : " + e.getMessage());
            return false;
        }
    }

    /**
     * Envoie un message au serveur
     * @param message Le contenu du message à envoyer
     */
    public void sendMessage(String message) {
        out.println("MSG:" + message);
        System.out.println("Message envoyé : " + message);
    }

    /**
     * Démarre un thread pour écouter les messages entrants
     */
    public void startMessageListener() {
        new Thread(() -> {
            try {
                String message;
                while ((message = in.readLine()) != null) {
                    if (message.startsWith("MSG:")) {
                        String[] parts = message.split(":", 3);
                        if (parts.length >= 3) {
                            System.out.println(parts[1] + ": " + parts[2]);
                        }
                    }
                }
            } catch (IOException e) {
                if (!socket.isClosed()) {
                    System.err.println("Connexion perdue : " + e.getMessage());
                }
            }
        }).start();
    }

    /**
     * Déconnecte le client du serveur
     */
    public void disconnect() {
        try {
            if (socket != null && !socket.isClosed()) {
                out.println("LOGOUT:" + username);
                socket.close();
                System.out.println("Déconnexion du serveur ClassCord");
            }
        } catch (IOException e) {
            System.err.println("Erreur lors de la déconnexion : " + e.getMessage());
        }
    }

    /**
     * Exemple d'utilisation du client ClassCord
     */
    public static void main(String[] args) {
        // Configuration du client
        String serverIp = "10.0.108.xx"; // Remplacer par l'IP réelle de l'hôte
        int serverPort = 12345;
        String username = "Vinceadr5";
        String password = "motdepasse";

        // Création et connexion du client
        ClassCordClient client = new ClassCordClient(serverIp, serverPort);
        if (client.connect()) {
            // Authentification
            if (client.login(username, password)) {
                // Démarrage de l'écoute des messages
                client.startMessageListener();

                // Envoi d'un message de test
                client.sendMessage("Bonjour à tous !");

                // Dans une application réelle, on attendrait les entrées de l'utilisateur
                // Pour cet exemple, on attend 10 secondes puis on se déconnecte
                try {
                    Thread.sleep(10000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                // Déconnexion
                client.disconnect();
            } else {
                System.err.println("Échec de l'authentification.");
            }
        } else {
            System.err.println("Impossible de se connecter au serveur.");
        }
    }
}
```

## Instructions d'utilisation

1. Compilation du client Java :

   ```bash
   javac ClassCordClient.java
   ```

2. Exécution du client :

   ```bash
   java ClassCordClient
   ```

3. Configuration personnalisée :
   - Modifiez les variables `serverIp`, `serverPort`, `username` et `password` dans la méthode `main` pour personnaliser la connexion.

## Protocole de communication

Le client et le serveur ClassCord communiquent en utilisant un protocole texte simple :

| Type de message | Format                    | Description                   |
| --------------- | ------------------------- | ----------------------------- |
| Connexion       | `LOGIN:username:password` | Demande d'authentification    |
| Message         | `MSG:contenu`             | Envoi d'un message            |
| Message reçu    | `MSG:expediteur:contenu`  | Message reçu d'un utilisateur |
| Déconnexion     | `LOGOUT:username`         | Notification de déconnexion   |

## Dépannage

Si la connexion échoue, vérifiez :

1. Que l'adresse IP et le port sont corrects
2. Que le serveur ClassCord est bien en cours d'exécution
3. Qu'aucun pare-feu ne bloque la connexion au port 12345
4. Que le nom d'utilisateur et le mot de passe sont valides

Pour tester la connectivité réseau basique, utilisez :

```bash
ping 10.0.108.xx
telnet 10.0.108.xx 12345
```
