from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import pickle

def save_data(athletes, page):
    """Sauvegarde les données des athlètes dans un fichier pickle."""
    with open(f"Berlin_2024_1-{page}.pkl", 'wb') as f:
        pickle.dump(athletes, f)
    print(f"Data saved for pages 1-{page}")

def fetch_athlete_data(driver, links):
    """Récupère les données d'un athlète donné."""
    athletes = []
    for index, link in enumerate(links):
        try:

            href = link.get_attribute('href')
            driver.get(href)
            
            # Attendre que la page se charge
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="cbox-main"]/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[10]/td[2]'))
            )
            
            # Analyse de la page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            name = soup.find('td', class_="f-__fullname").text.strip()
            age = soup.find('td', class_="f-age_class").text.strip()
            
            # Récupérer les splits
            splits = [soup.findAll('tr',class_=clas)[0].findAll('td',class_="time")[0].text if "52" not in clas 
                      else soup.findAll('tr',class_=clas)[0].findAll('td',class_=clas)[0].text
                      for clas in ["f-time_05","list-highlight f-time_10","f-time_15","list-highlight f-time_20","f-time_52","list-highlight f-time_25","f-time_30","list-highlight f-time_35","f-time_40","list-highlight f-time_finish_netto highlight"]]
            
            athlete_data = [name, age] + splits
            athletes.append(athlete_data)
            #print(f"Fetched data for athlete {name}")

            driver.back()  # Retourner à la page précédente

        except StaleElementReferenceException:
            print("StaleElementReferenceException encountered, skipping athlete")
        except Exception as e:
            print(f"Error fetching athlete data: {e}")
    
    return athletes

# Setup ChromeDriver
service = Service()
driver = webdriver.Chrome()


#athletes = []
page = 355
url = f'https://berlin.r.mikatiming.com/2024/?page={page}&event=BML_HCH3C0OH266&event_main_group=BMW+BERLIN+MARATHON&num_results=100&pid=list&search%5Bsex%5D=M&search%5Bage_class%5D=%25'

# URL de départ
driver.get(url)

page_selectors = [f"cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child({i}) > a" for i in [2,4,5]]+\
                [f"cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(6) > a"]*353

page_xpaths = [f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[2]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[4]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[5]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[7]/a']+\
              [f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[7]/a']*353

while page < 355:
    try:
        # Obtenir les liens vers les athlètes
        links = driver.find_elements(By.CSS_SELECTOR, '#cbox-main div ul li div h4 a')
        
        if links:
            #athletes += fetch_athlete_data(driver, links)
            #athletes = []
            for index, link in enumerate(links):
                #print(index)
                try:

                    href = link.get_attribute('href')
                    driver.get(href)
                    
                    # Attendre que la page se charge
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="cbox-main"]/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[10]/td[2]'))
                    )
                    
                    # Analyse de la page
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    name = soup.find('td', class_="f-__fullname").text.strip()
                    age = soup.find('td', class_="f-age_class").text.strip()
                    
                    # Récupérer les splits
                    try : splits = [soup.findAll('tr',class_=clas)[0].findAll('td',class_="time")[0].text if "52" not in clas 
                              else soup.findAll('tr',class_=clas)[0].findAll('td',class_=clas)[0].text
                              for clas in ["f-time_05","list-highlight f-time_10","f-time_15","list-highlight f-time_20","f-time_52","list-highlight f-time_25","f-time_30","list-highlight f-time_35","f-time_40","list-highlight f-time_finish_netto highlight"]]
                    except : splits = 9*['00:00:00']+[soup.findAll('tr',class_="list-highlight f-time_finish_netto highlight")[0].findAll('td',class_="time")[0].text]

                        
                    athlete_data = [name, age] + splits
                    athletes.append(athlete_data)
                    #print(f"Fetched data for athlete {name}")

                    driver.back()  # Retourner à la page précédente

                except StaleElementReferenceException:
                    print("StaleElementReferenceException encountered, skipping athlete")
                except Exception as e:
                    print(f"Error fetching athlete data: {e}")

            print(f"Processed page {page}")
            #driver.back()
        
        if page % 10 == 0:
            save_data(athletes, page)
        
        # Passer à la page suivante
        next_button = driver.find_element(By.XPATH, page_xpaths[page-1])
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(2) > a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(4) > a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(5) > a        //*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[6]/a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(7) > a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(7) > a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(7) > a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(7) > a
        #cbox-main > div:nth-child(4) > div.col-xs-4.col-sm-3.col-md-6 > div > ul > li:nth-child(7) > a
        #//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[8]/a
        #//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[8]/a
        if next_button:
            href = next_button.get_attribute('href')
            driver.get(href)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#cbox-main > div:nth-child(4) > div.col-xs-8.col-sm-9.col-md-6 > div > div > a:nth-child(1)'))
            )
        else:
            break

        page += 1

    except Exception as e:
        print(f"Error processing page {page}: {e}")
        break

# Sauvegarde finale des données
with open('Berlin_2024_final.pkl', 'wb') as f:
    pickle.dump(athletes, f)

#driver.quit()

import pickle  ; import re 
with open('Berlin_2024_final.pkl', 'rb') as f:
    athletes = pickle.load(f)
