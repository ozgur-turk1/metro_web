#!/bin/bash

# Activer l'environnement virtuel
source /home/ubuntu/metro_web/metro_web/bin/activate

# Dossier de logs
log_dir="/home/ubuntu/metro_web/logs"
mkdir -p "$log_dir"

# Fichier de log pour le script Selenium
selenium_log="$log_dir/selenium_$(date +'%Y-%m-%d').log"

# Exécuter le script Selenium avec xvfb-run et rediriger les logs
xvfb-run -a python3 /home/ubuntu/metro_web/web_sitemetro.py >> "$selenium_log"

# Récupérer la dernière ligne du fichier de log, qui devrait contenir le nom du fichier téléchargé
file_name=$(tail -n 1 "$selenium_log")

# Vérifier si un fichier a été téléchargé
if [ "$file_name" != "0" ] && [ -n "$file_name" ]; then
    echo "Fichier téléchargé: $file_name" >> "$selenium_log"
    # Fichier de log pour l'envoi d'email
    email_log="$log_dir/email_$(date +'%Y-%m-%d').log"
    
    # Exécuter le script d'envoi d'email avec le fichier téléchargé en argument et rediriger les logs
    python3 /home/ubuntu/metro_web/send_email.py "$file_name" >> "$email_log" 2>> "$email_log"
else
    echo "Aucun fichier téléchargé. Aucun email envoyé." >> "$selenium_log"
fi