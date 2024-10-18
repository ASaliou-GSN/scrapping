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


athletes = []
page = 1
#men
url = f'https://results.tcslondonmarathon.com/2022/?pid=list&fpid=list&lang=EN_CAP&event=MAS&num_results=1000&search%5Bsex%5D=M&search%5Bage_class%5D=%25&search_event=MAS'
#women 
#url = f'https://results.tcslondonmarathon.com/2022/?pid=list&fpid=list&lang=EN_CAP&event=MAS&num_results=1000&search%5Bsex%5D=W&search%5Bage_class%5D=%25&search_event=MAS'
#nonbin
#url = f'https://results.tcslondonmarathon.com/2022/?pid=list&fpid=list&lang=EN_CAP&event=MAS&num_results=1000&search%5Bsex%5D=D&search%5Bage_class%5D=%25&search_event=MAS'
#elite men
#url = f'https://results.tcslondonmarathon.com/2022/?pid=list&fpid=list&lang=EN_CAP&event=ELIT&num_results=1000&search%5Bsex%5D=M&search%5Bage_class%5D=%25&search_event=ELIT'
#elite women 
#url = f'https://results.tcslondonmarathon.com/2022/?pid=list&fpid=list&lang=EN_CAP&event=ELIT&num_results=1000&search%5Bsex%5D=W&search%5Bage_class%5D=%25&search_event=ELIT'

#starting url
driver.get(url)

page_xpaths = [f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[2]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[4]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[5]/a',f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[7]/a']+\
              [f'//*[@id="cbox-main"]/div[3]/div[2]/div/ul/li[7]/a']*353

while page <=29:
    try:
        
        #soup the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #extract hyperlinks to athletes pages
        links = soup.findAll('h4')
        
        for index, link in enumerate(links):
            try : 
            #connect to athlete details
                href = link.find('a')['href']
                driver.get('https://results.tcslondonmarathon.com/2022/'+href)
                
                
                #loading...
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cbox-main"]/div[2]/div[2]/div/div/a[1]'))
                )
                
                #read info
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                name = soup.find('td', class_="f-__fullname last").text.strip()
                age = soup.find('td', class_="f-_type_age_class last").text.strip()
                
                #get the splits
                try : splits = [soup.findAll('tr',class_=clas)[0].findAll('td',class_="time")[0].text if "52" not in clas 
                        else soup.findAll('tr',class_=clas)[0].findAll('td',class_=clas)[0].text
                        for clas in ["f-time_01","list-highlight f-time_02","f-time_03","list-highlight f-time_04","f-time_05 split","list-highlight f-time_06",
                                    "f-time_07","list-highlight f-time_08","f-time_09","list-highlight f-time_finish_netto highlight split"]]
                except : splits = 9*['00:00:00']+[soup.findAll('tr',class_="list-highlight f-time_finish_netto highlight split")[0].findAll('td',class_="time")[0].text]

                
                athlete_data = [name, age] + splits
                athletes.append(athlete_data)
                #print(f"Fetched data for athlete {name}")

                driver.back()  # Retourner à la page précédente

            #check the different erros : loading time too short or data corrupted ?
            except EC.StaleElementReferenceException:
                print("StaleElementReferenceException encountered, skipping athlete")
            except Exception as e:
                print(f"Error fetching athlete data: {e}")

        print(f"Processed page {page}")
        
        with open(f"mLondon_2022_{page}.pkl", 'wb') as f:
            pickle.dump(athletes, f)

        
        #click next page button, initiated at the beginning 
        next_button = driver.find_element(By.XPATH, page_xpaths[page-1])
        ###########
        #manual benchmark of buttons to seek the pattern to generate a full list
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
        #access next result page if available
        if next_button:
            href = next_button.get_attribute('href')
            driver.get(href)
            #loading...
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#cbox-main > div:nth-child(4) > div.col-xs-8.col-sm-9.col-md-6 > div > div > a:nth-child(1)'))
            )
        else:
            break
        page += 1

    except Exception as e:
        print(f"Error processing page {page}: {e}")
        break

#save the full athletes data in a global file
with open('mLondon_2022_final.pkl', 'wb') as f:
    pickle.dump(athletes, f)
