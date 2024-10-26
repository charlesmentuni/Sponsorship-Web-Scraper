import requests as rq
from bs4 import BeautifulSoup as bs
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_devpost():
    all_urls = []
    url = "https://devpost.com/hackathons"
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(url)
    time.sleep(2)
    # Wait until an element is present (e.g., an element with id 'content')
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "results-and-filters")),
        )
        
        soup = bs(driver.page_source, 'html.parser')
        for _ in range(1000):
            hackathons = soup.find_all(class_="hackathon-tile clearfix open mb-5")
            for hackathon in hackathons:
                if not  hackathon in all_urls:
                    all_urls.append(hackathon.find('a').get('href'))
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

    finally:
        driver.quit()
    
    with open("sponsor_urls.txt", "w") as file:
        file.seek(0)
        text_urls = "\n".join(x for x in all_urls)
        file.write(text_urls)
        file.close()

def get_sponsor_information(all_sponsors):
    result = dict()
    for s in all_sponsors:
        sponsor = s.parent
        sponsor_url = sponsor.get('href')
        if sponsor_url == None:
             continue
        sponsor_name = s.get('alt')
        sponsor_img = s.get('src')
        result[sponsor_url] = {
            'name' : sponsor_name,
            'logo' : sponsor_img
        }
    return result

def get_hackathon_information(soup):
    '''
    returns
        date of hackathon 
        number of participants
        keywords
        Location or online
    '''

    result = dict()
    keywords = []
    keyword_elements = soup.find(id='challenge-information').find_all(class_='info')[4].find_all(class_='label theme-label mr-1 mb-2')
    for keyword in keyword_elements:
        keywords.append(keyword.text.strip())
    


    result['keywords'] = keywords
    result['participant_number'] = int(soup.find(id='challenge-information').find_all(class_="info")[1].find_all('td')[3].find('strong').text)
    result['name'] = soup.find_all(class_ = "large-8 columns content")[0].find_all('h1')[0].text

    return result

def scrape_individual_hackathon(url):
    '''
        This function will return data from the sponsorships and what types of hackathons the companies sponsor
    '''
    result = dict()
    response = rq.get(url)
    soup = bs(response.text, 'html.parser')
    # Potentially parse the url so it doesn't have any sub folders in url
    # E.g https://a.com rather than https://a.com/hello/123
    # This is because we will be using this as a key in the json dictionary
    all_sponsors = soup.find_all(class_='sponsor_logo_img')
    result['sponsors'] = get_sponsor_information(all_sponsors)
    result['hackathon'] = get_hackathon_information(soup)

    return result

    
def add_sponsors(data):
    # if sponsor already exists then get number of hackathons * avg_number_of_participants
    '''
        {
            "a.com":
                {
                    number_of_participants over all hackathons : 5000,
                    number_of_hackathons : 12,
                    name : "The A Company",
                    logo: "img_link"
                    keywords : ['beginner friendly', 'ai'] 
                }
        }
        Average number of participants can be inferred
    '''
    with open("sponsors.json", "r+") as file:
        all_sponsors = json.load(file)
        for key in data["sponsors"].keys():
            if key in all_sponsors:
                 # perform calculations
                all_sponsors[key]['participants_num'] += data['hackathon']['participant_number']
                all_sponsors[key]['hackathon_num'] += 1
            else: 
                all_sponsors[key] = dict()
                all_sponsors[key]['participants_num'] = data['hackathon']['participant_number']
                all_sponsors[key]['hackathon_num'] = 1
                all_sponsors[key]['name'] = data['sponsors'][key]['name']
                all_sponsors[key]['logo'] = data['sponsors'][key]['logo']
                
        
        file.seek(0)
        json.dump(all_sponsors, file, indent=4)
    return 

if __name__ == '__main__':
        # scrape_devpost()
        example_url = "https://hackathon24.devpost.com/?ref_feature=challenge&ref_medium=discover"
        example_url1 = "https://codegeist.devpost.com/?ref_feature=challenge&ref_medium=discover"
        example_url2 = "https://api-world-2024-hackathon.devpost.com/?ref_feature=challenge&ref_medium=discover"

        r = scrape_individual_hackathon(example_url1)
        print(r['hackathon'])
        add_sponsors(r)
