#code of a scraper 
import requests
import os

def scrape_website(url):
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    print("Web Scraper")
