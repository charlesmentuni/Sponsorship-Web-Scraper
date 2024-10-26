import requests as rq
from bs4 import BeautifulSoup as bs

def scrape_devpost():
    url = "https://devpost.com/hackathons&page="
    for pageNum in range(1, 10):
        response=rq.get(url+str(pageNum))
        soup = bs(response.text, 'html.parser')
        print(soup)

def scrape_individual_hackathon(url):
    response = rq.get(url)
    soup = bs(response.text, 'html.parser')
    print(soup.find_all(id='challenge-sponsors-side').child())
    #print(soup.prettify())
    



if __name__ == '__main__':
        #scrape_devpost()
        example_url = "https://hackathon24.devpost.com/?ref_feature=challenge&ref_medium=discover"
        scrape_individual_hackathon(example_url)
