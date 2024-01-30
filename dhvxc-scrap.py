import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# WebDriver-Pfad (ersetzen Sie diesen mit dem Pfad zu Ihrem WebDriver)
driver_path = 'PFAD_ZUM_WEBDRIVER'

# WebDriver initialisieren
driver = webdriver.Chrome(driver_path)
load_dotenv()

# Erstellen einer Sitzung
session = requests.Session()

# Anmeldeinformationen
creds = {'uid': os.getenv('USERNAME'), 'pwd': os.getenv('PASSWORD')}
login_url = os.getenv('XC_LOGIN_URL')

# Webseite öffnen
driver.get(login_url)

# Warten, bis das JavaScript geladen ist
time.sleep(5)

# Benutzername und Passwort eingeben
username = driver.find_element_by_name('uid')
password = driver.find_element_by_name('pwd')

username.send_keys(creds.uid)
password.send_keys(creds.pwd)

# Formular absenden
password.send_keys(Keys.RETURN)

# Warten, um sicherzustellen, dass die Seite geladen ist
time.sleep(5)

# Ab hier können Sie weitere Aktionen auf der Seite durchführen

# Schließen Sie den Browser, wenn Sie fertig sind
driver.quit()



"""
# Einloggen
response = session.post(login_url, data=creds)

# Überprüfen, ob das Login erfolgreich war
if response.ok:
    # Download-Seite aufrufen
    download_page = session.get('https://de.dhv-xc.de/flights')

    # HTML mit BeautifulSoup parsen
    soup = BeautifulSoup(download_page.content, 'html.parser')

    # Finden Sie alle Download-Links
    for link in soup.find_all('a'):
        href = link.get('href')
        if "download" in href:
            download_link = 'https://de.dhv-xc.de/flights' + href
            file_response = session.get(download_link)

            # Datei speichern
            with open('downloaded_file', 'wb') as file:
                file.write(file_response.content)
else:
    print("Login fehlgeschlagen.")


"""