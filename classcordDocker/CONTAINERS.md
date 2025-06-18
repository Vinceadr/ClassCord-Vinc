touch# Guide Docker pour ClassCord

## Pourquoi Docker ?

Docker nous simplifie la vie avec ClassCord :

- On évite les problèmes du type "ça marche sur ma machine mais pas ailleurs"
- On installe tout d'un coup, pas besoin de configurer Python séparément
- Tout le monde peut lancer l'appli facilement, même sur un nouveau PC

## Comment build et run

### Pour construire l'image :

```bash
# Se placer dans le dossier du projet
cd ~/Documents/classcordDocker

# Construire l'image
docker-compose build
```

### Pour lancer l'application :

```bash
# Démarrer en arrière-plan
docker-compose up -d

# Pour voir les logs en direct
docker-compose logs -f classcord
```

### Pour arrêter l'application :

```bash
docker-compose down
```

## Ports à exposer

- **Port 12345** : C'est le port principal utilisé par ClassCord pour les connexions
- N'oubliez pas d'ouvrir ce port dans votre pare-feu

## Spécificités VM + NAT

Si vous utilisez une machine virtuelle avec NAT :

1. **Redirection de port** : Configurez votre VM pour rediriger le port 12345 vers votre machine hôte

   - Dans VirtualBox : Paramètres > Réseau > Avancé > Redirection de ports
   - Nom : ClassCord
   - Protocole : TCP
   - IP hôte : laisser vide
   - Port hôte : 12345
   - IP invité : laisser vide
   - Port invité : 12345

2. **Accès depuis l'extérieur** :

   - Dans la VM : utilisez `0.0.0.0:12345` (pas localhost) pour écouter sur toutes les interfaces
   - Depuis l'extérieur : connectez-vous à l'IP de la machine hôte sur le port 12345

3. **Problèmes courants** :
   - Si la connexion échoue, vérifiez que Docker écoute bien sur 0.0.0.0 et pas seulement sur localhost
   - Vérifiez que le pare-feu autorise les connexions sur le port 12345
