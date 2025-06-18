BACKUP_DIR="/home/vinc/backups/classcord"
CONTAINER_NAME="classcord-app"
DATE_FORMAT=$(date +%F-%H%M)
RETENTION_DAYS=7
# Création du répertoire de sauvegarde si nécessaire
mkdir -p $BACKUP_DIR

# Sauvegarde du fichier users.pkl depuis le conteneur
docker cp $CONTAINER_NAME:/app/users.pkl $BACKUP_DIR/users-$DATE_FORMAT.pkl
echo "Sauvegarde de users.pkl effectuée: users-$DATE_FORMAT.pkl"

# Sauvegarde des logs
docker cp $CONTAINER_NAME:/var/log/classcord $BACKUP_DIR/logs-$DATE_FORMAT
echo "Sauvegarde des logs effectuée: logs-$DATE_FORMAT"

# Nettoyage des anciennes sauvegardes (plus de 7 jours)
find $BACKUP_DIR -name "users-*.pkl" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "logs-*" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
echo "Nettoyage des sauvegardes de plus de $RETENTION_DAYS jours effectué"

# Création d'un fichier de vérification avec la date de dernière sauvegarde
echo "Dernière sauvegarde: $(date)" > $BACKUP_DIR/last_backup_info.txt