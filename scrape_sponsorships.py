import requests as rq
from bs4 import BeautifulSoup as bs
import json


def scrape_devpost():
    url = "https://devpost.com/hackathons&page="
    for pageNum in range(1, 10):
        response=rq.get(url+str(pageNum))
        soup = bs(response.text, 'html.parser')
        print(soup)

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

    result['participant_number'] = soup.find(id='challenge-information').find_all(class_="info")[1].find_all('td')[3].find('strong').text
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
                file.close() 
            else: 
                all_sponsors[key] = dict()
                all_sponsors[key]['participants_num'] = data['hackathon']['participant_number']
                all_sponsors[key]['hackathon_num'] = 1
                all_sponsors[key]['name'] = data['sponsors'][key]['name']
        
        file.seek(0)
        json.dump(all_sponsors, file)
    return 

if __name__ == '__main__':
        #scrape_devpost()
        example_url = "https://hackathon24.devpost.com/?ref_feature=challenge&ref_medium=discover"
        example_url1 = "https://codegeist.devpost.com/?ref_feature=challenge&ref_medium=discover"
        example_url2 = "https://api-world-2024-hackathon.devpost.com/?ref_feature=challenge&ref_medium=discover"
        r = scrape_individual_hackathon(example_url2)
        add_sponsors(r)
