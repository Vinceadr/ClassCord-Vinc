#!/bin/bash
# Script de sauvegarde pour ClassCord

# Configuration
BACKUP_DIR="/home/vinc/backups/classcord"
SOURCE_DIR="/home/vinc/Documents/classcordDocker"
DATE_FORMAT=$(date +%F-%H%M)
RETENTION_DAYS=7

# Création du répertoire de sauvegarde si nécessaire
mkdir -p $BACKUP_DIR
sudo chown vinc:vinc $BACKUP_DIR
chmod 755 $BACKUP_DIR

echo "Démarrage sauvegarde: $(date)"

# Sauvegarde du fichier users.pkl
if [ -f "$SOURCE_DIR/users.pkl" ]; then
    cp "$SOURCE_DIR/users.pkl" "$BACKUP_DIR/users-$DATE_FORMAT.pkl"
    echo "Sauvegarde de users.pkl effectuée: users-$DATE_FORMAT.pkl"
else
    echo "Attention: $SOURCE_DIR/users.pkl n'existe pas"
    
    # Recherche du fichier users.pkl dans le répertoire courant et ses sous-répertoires
    FOUND_FILES=$(find "$SOURCE_DIR" -name "users.pkl" -type f 2>/dev/null)
    
    if [ -n "$FOUND_FILES" ]; then
        echo "Fichiers users.pkl trouvés dans d'autres emplacements:"
        echo "$FOUND_FILES"
        
        # Sauvegarde du premier fichier trouvé
        FIRST_FILE=$(echo "$FOUND_FILES" | head -n 1)
        cp "$FIRST_FILE" "$BACKUP_DIR/users-$DATE_FORMAT.pkl"
        echo "Sauvegarde effectuée depuis: $FIRST_FILE"
    else
        echo "Aucun fichier users.pkl trouvé dans $SOURCE_DIR ou ses sous-répertoires"
    fi
fi

# Sauvegarde du fichier docker-compose.yml si présent
if [ -f "$SOURCE_DIR/docker-compose.yml" ]; then
    cp "$SOURCE_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose-$DATE_FORMAT.yml"
    echo "Sauvegarde de docker-compose.yml effectuée"
fi

# Sauvegarde des autres fichiers importants du projet
for file in "$SOURCE_DIR"/*.py "$SOURCE_DIR"/*.md "$SOURCE_DIR"/*.sh; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$BACKUP_DIR/$filename-$DATE_FORMAT"
        echo "Sauvegarde de $filename effectuée"
    fi
done

# Nettoyage des anciennes sauvegardes
find $BACKUP_DIR -name "*.pkl" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.yml" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.py" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.md" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.sh" -type f -mtime +$RETENTION_DAYS -delete
echo "Nettoyage des sauvegardes de plus de $RETENTION_DAYS jours effectué"

# Création d'un fichier de vérification avec la date de dernière sauvegarde
echo "Dernière sauvegarde: $(date)" > $BACKUP_DIR/last_backup_info.txt
echo "Fin de la sauvegarde: $(date)"

# Liste des fichiers sauvegardés
echo "Fichiers sauvegardés:"
ls -lh $BACKUP_DIR | grep "$DATE_FORMAT"