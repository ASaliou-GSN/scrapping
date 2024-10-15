from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import pickle

athletes = []

with open('Tokyo_2023_691-700.pkl', 'rb') as f:
    athletes = pickle.load(f)

# Setup ChromeDriver
service = Service()
driver = webdriver.Chrome()

# Open the results page
url = 'https://www.marathon.tokyo/2023/result/index.php'
driver.get(url)

# Click the search button
search_button = driver.find_element(By.ID, 'btn_submit')
search_button.click()

page = 700
while len(athletes) <= 36751:
    # Get all links to athlete details
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:detail')]")
    total_links = len(links)  # Store the total number of links

    for index in range(total_links):
        try:
            # Use the index to fetch the link and execute the script
            link = links[index]
            href = link.get_attribute('href')
            driver.execute_script(href)

            # Wait for the athlete detail page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Parse the tables
            tables = soup.findAll('table')
            athlete_data = [pd.read_html(StringIO(str(table)))[0] for table in tables[:3]]  # Limit to the first three tables
            athletes.append(athlete_data)

            driver.back()  # Go back to the results page

            # Wait for the results page to reload
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'btn_submit')))
            
            # Re-fetch the links after going back to the results page
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:detail')]")
        except StaleElementReferenceException:
            print("StaleElementReferenceException encountered, re-fetching links...")
            # Re-fetch links on stale element exception
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:detail')]")

    print(f"Processed page {page}")  # Print the processed page number
    page += 1
    if not page%10 : 
        # Save the athletes data to a pickle file
        with open(f"Tokyo_2023_{page+1-10}-{page}.pkl", 'wb') as f:
            pickle.dump(athletes, f)

    # Navigate to the next page
    next_page_button = driver.find_elements(By.XPATH, f"//a[contains(@href, 'page({page})')]")
    if next_page_button:
        next_page_button[0].click()
        # Wait for the new page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'btn_submit')))
    else:
        break  # No more pages to process

driver.quit()

# Save the athletes data to a pickle file
with open('Tokyo_2023.pkl', 'wb') as f:
    pickle.dump(athletes, f)
    
    
    


