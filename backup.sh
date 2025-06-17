#!/bin/bash

# Sozlamalar
DB_NAME="db_name"
DB_USER="postgres"
BACKUP_DIR="/home/backup"
MEDIA_DIR="/home/project/media"

# Sana
DATE=$(date +%F)

# Database backup
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
rsync -av --progress $MEDIA_DIR $BACKUP_DIR/media_backup_$DATE

# .env backup
cp /home/project/.env $BACKUP_DIR/.env_backup_$DATE

echo "Backup tugadi: $DATE"
