import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime


def search_jobs(job_title):
    url = "https://www.fhf.fr/emploi/search?type"

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)

    input_keyword = driver.find_element(By.ID, 'edit-keyword--3')
    input_keyword.send_keys(job_title)
    driver.execute_script(
        "arguments[0].click();", driver.find_element(By.ID, 'edit-submit--4'))
    time.sleep(2)

    return driver


def scrape_job_details(driver):
    data = []

    while True:
        offre_links = driver.find_elements(By.CSS_SELECTOR, 'a.btn.btn-link')
        for offre_link in offre_links:
            driver.execute_script(
                "window.open('" + offre_link.get_attribute('href') + "');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            details_section = soup.find('div', class_='article__content')

            poste_propose_elem = details_section.find(
                'div', class_='section-title', string='Poste proposé')
            poste_propose = poste_propose_elem.next_sibling.strip() if poste_propose_elem else None

            contrat_elem = details_section.find(
                'div', class_='section-title', string='Contrat')
            contrat = contrat_elem.next_sibling.strip() if contrat_elem else None

            descriptif_elem = details_section.find(
                'div', class_='section-title', string='Descriptif')
            descriptif = descriptif_elem.next_sibling.strip() if descriptif_elem else None

            personne_contact_elem = details_section.find(
                'div', class_='section-title', string='Personne à contacter')
            if personne_contact_elem:
                personne_contact = personne_contact_elem.find_next(
                    'div', class_='contact')
                if personne_contact:
                    if personne_contact.find('div', class_='contact-name'):
                        nom_contact = personne_contact.find(
                            'div', class_='contact-name').next_sibling.strip()
                    else:
                        nom_contact = personne_contact.text.strip()
                    email_contact = personne_contact.find(
                        'a', href=True)['href'].split(':')[-1]
                else:
                    nom_contact = None
                    email_contact = None
            else:
                nom_contact = None
                email_contact = None

            etablissement_elem = details_section.find(
                'div', class_='section-title', string='Etablissement')
            etablissement = etablissement_elem.find_next_sibling().get_text(
                strip=True) if etablissement_elem else None

            publication_info = soup.find('div', class_='publication-info')
            publication_date_div = publication_info.find(
                lambda tag: tag.name == 'div' and 'Publié le' in tag.get_text())
            deadline_date_div = publication_info.find(
                lambda tag: tag.name == 'div' and 'Date de limite de candidatures' in tag.get_text())

            publication_date = publication_date_div.get_text().split(
                'Publié le ')[1].strip() if publication_date_div else None
            deadline_date = deadline_date_div.get_text().split(
                'Date de limite de candidatures ')[1].strip() if deadline_date_div else None
            data.append({
                "poste_propose": poste_propose,
                "contrat": contrat,
                "descriptif": descriptif,
                "nom_contact": nom_contact,
                "email_contact": email_contact,
                "etablissement": etablissement,
                "publication_date": publication_date,
                "deadline_date": deadline_date
            })

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        try:
            next_page_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'li.pager__item--next a'))
            )
            driver.execute_script("arguments[0].click();", next_page_link)
            time.sleep(2)
        except:
            break

    return data


def clean_data(data):
    cleaned_data = []
    for entry in data:
        cleaned_entry = {}
        for key, value in entry.items():
            if value is not None:
                cleaned_value = value.replace('\n', '')
            else:
                cleaned_value = None
            cleaned_entry[key] = cleaned_value
        cleaned_data.append(cleaned_entry)
    return cleaned_data


def export_to_csv(data, file_name):
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        headers = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import csv
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from datetime import datetime


# def search_jobs(job_title):
#     url = "https://www.fhf.fr/emploi/search?type"

#     options = Options()
#     # Exécuter le navigateur en mode headless
#     options.add_argument('--headless')
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     time.sleep(2)

#     input_keyword = driver.find_element(By.ID, 'edit-keyword--3')
#     input_keyword.send_keys(job_title)
#     driver.execute_script(
#         "arguments[0].click();", driver.find_element(By.ID, 'edit-submit--4'))
#     time.sleep(2)

#     return driver


# def scrape_job_details(driver):
#     data = []

#     while True:
#         offre_links = driver.find_elements(By.CSS_SELECTOR, 'a.btn.btn-link')
#         for offre_link in offre_links:
#             driver.execute_script(
#                 "window.open('" + offre_link.get_attribute('href') + "');")
#             driver.switch_to.window(driver.window_handles[-1])
#             time.sleep(2)

#             html_content = driver.page_source
#             soup = BeautifulSoup(html_content, 'html.parser')
#             details_section = soup.find('div', class_='article__content')

#             poste_propose_elem = details_section.find(
#                 'div', class_='section-title', string='Poste proposé')
#             poste_propose = poste_propose_elem.next_sibling.strip() if poste_propose_elem else None

#             contrat_elem = details_section.find(
#                 'div', class_='section-title', string='Contrat')
#             contrat = contrat_elem.next_sibling.strip() if contrat_elem else None

#             descriptif_elem = details_section.find(
#                 'div', class_='section-title', string='Descriptif')
#             descriptif = descriptif_elem.next_sibling.strip() if descriptif_elem else None

#             personne_contact_elem = details_section.find(
#                 'div', class_='section-title', string='Personne à contacter')
#             if personne_contact_elem:
#                 personne_contact = personne_contact_elem.find_next(
#                     'div', class_='contact')
#                 if personne_contact:
#                     if personne_contact.find('div', class_='contact-name'):
#                         nom_contact = personne_contact.find(
#                             'div', class_='contact-name').next_sibling.strip()
#                     else:
#                         nom_contact = personne_contact.text.strip()
#                     email_contact = personne_contact.find(
#                         'a', href=True)['href'].split(':')[-1]
#                 else:
#                     nom_contact = None
#                     email_contact = None
#             else:
#                 nom_contact = None
#                 email_contact = None

#             etablissement_elem = details_section.find(
#                 'div', class_='section-title', string='Etablissement')
#             etablissement = etablissement_elem.find_next_sibling().get_text(
#                 strip=True) if etablissement_elem else None
#             # Extraction de la date de publication et de la date limite de candidature
#             publication_info = soup.find('div', class_='publication-info')
#             publication_date_div = publication_info.find(
#                 lambda tag: tag.name == 'div' and 'Publié le' in tag.get_text())
#             deadline_date_div = publication_info.find(
#                 lambda tag: tag.name == 'div' and 'Date de limite de candidatures' in tag.get_text())

#             # Convertir les dates en objets datetime si elles sont disponibles
#             publication_date = publication_date_div.get_text().split(
#                 'Publié le ')[1].strip() if publication_date_div else None
#             deadline_date = deadline_date_div.get_text().split(
#                 'Date de limite de candidatures ')[1].strip() if deadline_date_div else None
#             data.append({
#                 "poste_propose": poste_propose,
#                 "contrat": contrat,
#                 "descriptif": descriptif,
#                 "nom_contact": nom_contact,
#                 "email_contact": email_contact,
#                 "etablissement": etablissement,
#                 "publication_date": publication_date,
#                 "deadline_date": deadline_date
#             })

#             driver.close()
#             driver.switch_to.window(driver.window_handles[0])

# # Attendre que le lien vers la page suivante devienne disponible
#         try:
#             next_page_link = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, 'li.pager__item--next a'))
#             )
#             driver.execute_script("arguments[0].click();", next_page_link)
#             time.sleep(2)
#         except:
#             break

#     return data


# def clean_data(data):
#     cleaned_data = []
#     for entry in data:
#         cleaned_entry = {}
#         for key, value in entry.items():
#             if value is not None:
#                 cleaned_value = value.replace('\n', '')
#             else:
#                 cleaned_value = None
#             cleaned_entry[key] = cleaned_value
#         cleaned_data.append(cleaned_entry)
#     return cleaned_data


# def export_to_csv(data, file_name):
#     with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
#         headers = data[0].keys()
#         writer = csv.DictWriter(csvfile, fieldnames=headers)
#         writer.writeheader()
#         for row in data:
#             writer.writerow(row)


# if __name__ == "__main__":
#     job_title = "infirmier"
#     driver = search_jobs(job_title)
#     job_data = scrape_job_details(driver)
#     cleaned_job_data = clean_data(job_data)
#     # print(cleaned_job_data)
#     driver.quit()

#     file_name = f"{job_title}_jobs.csv"
#     export_to_csv(cleaned_job_data, file_name)
