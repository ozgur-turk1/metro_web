import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
import shutil  # Pour renommer le fichier
from datetime import datetime  # Pour obtenir la date actuelle

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

download_dir = "/home/ubuntu/metro_web/download"

# Initialiser le WebDriver
chrome_options  = Options()
chrome_options.add_argument("--headless")  # Mode headless
chrome_prefs = {
    "download.default_directory": download_dir,  # Dossier de téléchargement
    "download.prompt_for_download": False,  # Ne pas demander où enregistrer
    "download.directory_upgrade": True,  # Autoriser la mise à niveau du répertoire de téléchargement
    "safebrowsing.enabled": True  # Activer le téléchargement sans le blocage SafeBrowsing
}
chrome_options.add_experimental_option("prefs", chrome_prefs)

# Démarrer ChromeDriver
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Firefox(service=service, options=chrome_options )

# Lecture du JSON pour les informations de connexion à l'espace client
try:
    with open("/home/ubuntu/metro_web/data_metro.json", "r") as f:
        data = json.load(f)
except Exception as e:
    logging.error(f"Erreur lors de la lecture du fichier JSON : {e}")
    driver.quit()
    exit(1)


# Générer la date du jour pour le nom du fichier
current_date = datetime.now().strftime("%Y-%m-%d")

# Chemin de l'URL de connexion et du dossier de téléchargement
connexion_url = "https://idam.metro.fr/web/Signin?passwordless=true&scope=profile+email+openid&locale_id=fr-FR&redirect_uri=https%3A%2F%2Fwww.metro.fr%2Fmetro%2Fservices%2Fidam%2Faccess_token%3Fru%3DZnFjWGJ6NkhOcjRENVJlNE40SDNQYkhkVVZLMGxSSlhmc3F4Q0QzUW0wZHoxWFVkY0lZMVgvZ2o1YnE3N0dsUVNpNmw3UT09&client_id=NEXTCMS&country_code=FR&realm_id=SHOP_FR&user_type=CUST&DR-Trace-ID=idam-trace-id&response_type=code"
doc_url = "https://docs.metro.fr"
new_file_name = f"factures_metro_{current_date}.zip"  # Nom personnalisé pour le fichier téléchargé avec la date

def get_latest_file(download_dir):
    """
    Obtenir le fichier le plus récemment modifié dans le répertoire de téléchargement.
    """
    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith(".zip")]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


try:
    # Naviguer vers la page de connexion
    logging.info("Naviguer vers la page de connexion")
    driver.get(connexion_url)

    # Attendre que la page se charge
    time.sleep(5)

    # Clic sur le bouton de refus des cookies
    # item = driver.execute_script('''return document.querySelector('cms-cookie-disclaimer').shadowRoot.querySelector('button[class="btn-secondary reject-btn field-reject-button-name"]')''')
    # item.click()
    logging.info("Clic sur le bouton de refus des cookies")

    # Trouver les champs de saisie pour le nom d'utilisateur et le mot de passe
    username_field = driver.find_element(By.ID, "user_id")
    password_field = driver.find_element(By.ID, "password")

    # Entrer les informations d'identification
    logging.info("Entrée des informations de connexion")
    username_field.send_keys(data["user_id"])
    password_field.send_keys(data["password"])

    # Soumettre le formulaire
    password_field.send_keys(Keys.RETURN)

    # Attendre la redirection
    time.sleep(5)

    logging.info("Connexion réussie et accès à l'espace client.")

    driver.get(doc_url)
    time.sleep(5)
    invoices = driver.find_elements(By.CLASS_NAME, "css-upnin5")
    download = 0
    next_page = True

    while next_page:
        # Vérifie les factures sur la page
        for invoice in invoices:
            invoice_not_downloaded = invoice.find_elements(By.TAG_NAME, "td")[1]

            if "dgJGMJ" in invoice_not_downloaded.get_attribute("class"):
                download += 1                 
                logging.info(f"Téléchargement de la facture: {invoice_not_downloaded.get_attribute('textContent')}")
                id_invoice = invoice.find_element(By.CLASS_NAME, "css-13wg1tp").get_attribute("for")
                element = driver.find_element(By.ID, id_invoice)
                driver.execute_script("arguments[0].click();", element)
            else:
                next_page = False
                break
        break

    # Clic sur le bouton de téléchargement si des factures sont à télécharger
    if download:
        e = driver.find_element(By.XPATH, '//button[@data-testid="downloadSelectedInvoicesButton"]')
        e.click()

        time.sleep(5)

        downloaded_file_path = get_latest_file(download_dir)
        new_file_path = os.path.join(download_dir, new_file_name)
        shutil.move(downloaded_file_path, new_file_path)

        logging.info(f"Fichier {new_file_path} téléchargé avec succès : {download} factures dans l'archive")
        print(new_file_path)
    else:
        logging.info("Aucune nouvelle facture trouvé.")
        print(0)
   
    # else:
    #     logging.warning("Échec de l'accès à l'espace client.")

except Exception as e:
    logging.error(f"Une erreur s'est produite : {e}")

finally:
    # Fermer le navigateur
    logging.info("Fermeture du navigateur")
    driver.quit()