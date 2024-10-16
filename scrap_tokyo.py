#code to scrap Tokyo Marathon data
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import pickle

#%%
#initiate a list of athletes
page = 1 #must be modulo 10
if page == 1 : athletes = []
#if need to restart the scraping 
else : 
    with open(f'Tokyo_2023_{page+1}-{page}.pkl', 'rb') as f:
        athletes = pickle.load(f)


#%%
#! website requires js execution -> use of selenium (driver) instead of resquests
#setup ChromeDriver
service = Service()
driver = webdriver.Chrome()

#open the results page
url = 'https://www.marathon.tokyo/2023/result/index.php'
driver.get(url)

#click the search button
search_button = driver.find_element(By.ID, 'btn_submit')
search_button.click()

#we fill the athletes data
while len(athletes) <= 36751:
    #fet all links to athlete details on the page
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:detail')]")
    total_links = len(links)  #tore the total number of links

    for index in range(total_links):
        #ensure no failing with a try
        try:
            #access athlete details page via execution of href
            link = links[index]
            href = link.get_attribute('href')
            driver.execute_script(href)

            #loading... with the details table as ref point
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
   
            #parse html details and extract table
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.findAll('table')
            
            #read athletes data from the table
            athlete_data = [pd.read_html(StringIO(str(table)))[0] for table in tables[:3]]  # Limit to the first three tables
            athletes.append(athlete_data)

            driver.back()  #page back to list of results

            #loading... with page back button (bottom) as ref point
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'btn_submit')))
            
            #RE-fetch (!!) all links to athlete details on the page
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:detail')]")
        #if fail, go back to fetch and next
        except EC.StaleElementReferenceException:
            print("StaleElementReferenceException encountered, re-fetching links...")
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:detail')]")

    print(f"Processed page {page}") #check every page
    page += 1 #next page
    
    #every 10 pages, save the data in a pickle file
    if not page%10 : 

        with open(f"Tokyo_2023_{page+1-10}-{page}.pkl", 'wb') as f:
            pickle.dump(athletes, f)

    #go to next page to restart the loop
    next_page_button = driver.find_elements(By.XPATH, f"//a[contains(@href, 'page({page})')]")
    if next_page_button:
        next_page_button[0].click()
        #loading
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'btn_submit')))
    else:
        break  #done with all ages

#save the full athletes data in a global file
with open('Tokyo_2023.pkl', 'wb') as f:
    pickle.dump(athletes, f)
    
#quit driver, comment in night scrapping, to be sure in the morning :)
driver.quit()

    


