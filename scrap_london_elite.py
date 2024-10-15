from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import pickle


# Setup ChromeDriver
service = Service()
driver = webdriver.Chrome()


athletes = []
#men_elite
#url = f'https://results.tcslondonmarathon.com/2024/?num_results=1000&pid=list&search%5Bsex%5D=M&search%5Bage_class%5D=%25&event=ELIT&favorite_add=9TG2O3HQ443609'
#women_elite
url = f'https://results.tcslondonmarathon.com/2024/?pid=list&fpid=list&lang=EN_CAP&event=ELIT&num_results=1000&pidp=start&search%5Bsex%5D=W&search%5Bage_class%5D=%25&search_event=ELIT'

# URL de départ
driver.get(url)

# Obtenir les liens vers les athlètes
links = driver.find_elements(By.CSS_SELECTOR, '#cbox-main > div.col-sm-12.row-xs > ul > li:nth-child(2) > div.col-xs-12.col-sm-12.col-md-5.list-field-wrap > div > h4 > a')

soup = BeautifulSoup(driver.page_source, 'html.parser')
links = soup.findAll('h4')
for index, link in enumerate(links):

    href = link.find('a')['href']
    driver.get('https://results.tcslondonmarathon.com/2024/'+href)
    
    
    # Attendre que la page se charge
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="cbox-main"]/div[2]/div[2]/div/div/a[1]'))
    )
    
    # Analyse de la page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    name = soup.find('td', class_="f-__fullname").text.strip()
    age = soup.find('td', class_="f-age_class").text.strip()
    
    # Récupérer les splits
    try : splits = [soup.findAll('tr',class_=clas)[0].findAll('td',class_="time")[0].text if "52" not in clas 
              else soup.findAll('tr',class_=clas)[0].findAll('td',class_=clas)[0].text
              for clas in ["f-time_01","list-highlight f-time_02","f-time_03","list-highlight f-time_04","f-time_05 split","list-highlight f-time_06",
                           "f-time_07","list-highlight f-time_08","f-time_09","list-highlight f-time_finish_netto highlight split"]]
    except : splits = 9*['00:00:00']+[soup.findAll('tr',class_="list-highlight f-time_finish_netto highlight split")[0].findAll('td',class_="time")[0].text]

    
    athlete_data = [name, age] + splits
    athletes.append(athlete_data)
    #print(f"Fetched data for athlete {name}")

    driver.back()  # Retourner à la page précédente
    
# Sauvegarde finale des données
with open('wLondon_2024_final.pkl', 'wb') as f:
    pickle.dump(athletes, f)
    
#for clas in ["f-time_01","list-highlight f-time_02","f-time_03","list-highlight f-time_04","f-time_05 split","list-highlight f-time_06",
#             "f-time_07","list-highlight f-time_08","f-time_09","list-highlight f-time_finish_netto highlight split"] :
#    print(soup.findAll('tr',class_=clas)[0].findAll('td',class_="time")[0].text)




