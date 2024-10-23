# Récupération Automatique des Factures Metro.fr

Ce programme récupère automatiquement les dernières factures non déjà téléchargées depuis le site [Metro.fr](https://www.metro.fr), puis envoie les factures par email à une adresse spécifiée. Le programme est actuellement déployé sur une instance **AWS EC2**.

## Fonctionnalités

- **Connexion automatique à Metro.fr** : Le programme se connecte à votre compte client Metro en utilisant les informations d'identification stockées de manière sécurisée.
- **Téléchargement des factures** : Il vérifie quelles factures n'ont pas encore été téléchargées et télécharge uniquement les nouvelles factures.
- **Envoi par email** : Après le téléchargement, les factures sont envoyées par email via un service de messagerie configuré (comme AWS SES ou Gmail).
- **Déploiement automatique** : Le programme est exécuté régulièrement sur une instance **AWS EC2** via une tâche **cron**.

## Installation et Configuration

### Pré-requis

- Python 3.8 ou supérieur
- Environnement virtuel Python (`venv`)
- Bibliothèques Python nécessaires : `selenium`, `requests`, `python-dotenv`, `boto3`, `beautifulsoup4`, etc.
- Serveur de messagerie (comme AWS SES ou une configuration Gmail)

## Déploiement sur AWS EC2
Le programme est déployé sur une instance AWS EC2 et s'exécute automatiquement grâce à une tâche cron qui vérifie les nouvelles factures une fois par mois (ou selon la fréquence définie).

