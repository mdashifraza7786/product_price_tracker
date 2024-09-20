import requests
from bs4 import BeautifulSoup

# Scrape product details including price
def scrape_product_details(url):
    if 'amazon' in url:
        return scrape_amazon(url)
    elif 'flipkart' in url:
        return scrape_flipkart(url)
    else:
        raise ValueError("Unsupported marketplace URL")
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.flipkart.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
        'Connection': 'keep-alive'
    }

def scrape_flipkart(url):
    headers = get_headers()
    
    response = requests.get(url, headers=headers)
    print(f"Flipkart response status code: {response.status_code}")
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch Flipkart product page. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    print(soup.prettify()[:500])  # Print the first 500 characters of the HTML
    
    price_element = soup.find('div', {'class': 'Nx9bqj CxhGGd'})
    if not price_element:
        raise ValueError("Could not find price on Flipkart page")
    
    product_name_element = soup.find('span', {'class': 'VU-ZEz'})
    if not product_name_element:
        raise ValueError("Could not find product name on Flipkart page")
    
    price = price_element.text.strip().replace('₹', '').replace(',', '')
    product_name = product_name_element.text.strip()
    
    return {
        'name': product_name,
        'price': float(price)
    }

def scrape_amazon(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    
    print(f"Flipkart response status code: {response.status_code}")
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch Flipkart product page. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    
    # Debugging: print out part of the HTML to ensure the scraper is getting the correct data
    print(soup.prettify()[:500])  # Print the first 500 characters of the HTML

    # Extract price
    price_element = soup.find('div', {'class': '_30jeq3'})
    if not price_element:
        raise ValueError("Could not find price on Flipkart page")
    
    # Extract product name
    product_name_element = soup.find('span', {'class': 'B_NuCI'})
    if not product_name_element:
        raise ValueError("Could not find product name on Flipkart page")
    
    # Clean the data and return
    price = price_element.text.strip().replace('₹', '').replace(',', '')
    product_name = product_name_element.text.strip()
    
    return {
        'name': product_name,
        'price': float(price)
    }
