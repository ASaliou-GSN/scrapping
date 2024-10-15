#test to scrap Chicago
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


#athletes = []
page = 1
url = f'https://results.chicagomarathon.com/2024/?page={page}&event=MAR&event_main_group=runner&num_results=1000&pid=list&search%5Bsex%5D=M&search%5Bage_class%5D=%25'

# URL de départ
driver.get(url)

page_xpaths = [f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[2]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[4]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[5]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[7]/a']+\
              [f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[7]/a']*353

while page < 355:
    try:
        # Obtenir les liens vers les athlètes
        links = driver.find_elements(By.CSS_SELECTOR, '#cbox-main div ul li div h4 a')
