import os
import json
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Vérifier que le chemin du fichier est passé en argument
if len(sys.argv) < 2:
    logging.error("Erreur : vous devez spécifier le fichier à envoyer en pièce jointe.")
    sys.exit(1)

file_path = sys.argv[1]

# Charger les données depuis le fichier JSON pour obtenir les détails de l'email
try:
    with open("/home/ubuntu/metro_web/email_data.json", "r") as f:
        email_data = json.load(f)
    logging.info("Données de configuration d'email chargées avec succès.")
except FileNotFoundError:
    logging.error("Erreur : le fichier email_data.json est introuvable.")
    sys.exit(1)
except json.JSONDecodeError:
    logging.error("Erreur : échec du décodage du fichier JSON.")
    sys.exit(1)

# Extraire les données du fichier JSON
sender = email_data['sender']
recipient = email_data['recipient']
subject = email_data['subject']
body_text = email_data['body_text']
aws_region = email_data['aws_region']

# Vérifier si le fichier existe
if os.path.exists(file_path):
    logging.info(f"Fichier à envoyer : {file_path}")

    # Connexion à AWS SES
    ses_client = boto3.client('ses', region_name=aws_region)

    # Créer l'email
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    # Ajouter le corps du message
    body = MIMEText(body_text, "plain")
    msg.attach(body)

    # Ajouter la pièce jointe (le fichier téléchargé)
    try:
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}",
            )
            msg.attach(part)
        logging.info(f"Pièce jointe ajoutée : {file_path}")
    except Exception as e:
        logging.error(f"Erreur lors de l'ajout de la pièce jointe : {e}")
        sys.exit(1)

    # Envoyer l'email via AWS SES
    try:
        response = ses_client.send_raw_email(
            Source=sender,
            Destinations=[recipient],
            RawMessage={"Data": msg.as_string()},
        )
        logging.info(f"Email envoyé avec succès! Message ID: {response['MessageId']}")
    except ClientError as e:
        logging.error(f"Erreur lors de l'envoi de l'email : {e.response['Error']['Message']}")
        sys.exit(1)
else:
    logging.error(f"Le fichier {file_path} n'existe pas. Aucune pièce jointe envoyée.")
    sys.exit(1)