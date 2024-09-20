import requests
from bs4 import BeautifulSoup
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
import datetime
import os
import random



def notify_user(db, email, product_id):
    product = db.products.find_one({'_id': ObjectId(product_id)})
    if product:
        send_email(email, product)
    else:
        print(f"Product with ID {product_id} not found.")

def send_email(to_email, product):
    msg = MIMEText(f"Price update for {product['url']}. Current price: {product['current_price']}")
    msg['Subject'] = 'Price Update'
    msg['From'] = os.getenv('EMAIL_ADDRESS')
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))
            server.sendmail(os.getenv('EMAIL_ADDRESS'), [to_email], msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_prices(db):
    products = db['products'].find()
    for product in products:
        current_price = fetch_current_price(product['product_url'])
        if current_price is not None and price_changed(product['current_price'], current_price):
            db.products.update_one(
                {'_id': ObjectId(product['_id'])},
                {'$set': {
                    'current_price': current_price,
                    'last_checked': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }}
            )
            users = db.users.find({'_id': product['user_id']})
            # for user in users:
            #     notify_user(db, user['email'], product['_id'])

def fetch_current_price(url):
    try:
        # Fetch the current price from the URL
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        # Scrape the product details from the response
        product_details = scrape_product_details(url)
        return product_details['price']
    except Exception as e:
        print(f"Failed to fetch current price: {e}")
        return None


def price_changed(old_price, new_price):
    return old_price != new_price

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
        'Connection': 'keep-alive'
    }

def scrape_product_details(url):
    if 'amazon' in url:
        return scrape_amazon(url)
    elif 'flipkart' in url:
        return scrape_flipkart(url)
    else:
        raise ValueError("Unsupported marketplace URL")

def scrape_flipkart(url):
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch Flipkart product page. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
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
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch Amazon product page. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    price_element = soup.find('span', {'id': 'priceblock_ourprice'})
    if not price_element:
        raise ValueError("Could not find price on Amazon page")
    
    product_name_element = soup.find('span', {'id': 'productTitle'})
    if not product_name_element:
        raise ValueError("Could not find product name on Amazon page")
    
    price = price_element.text.strip().replace('$', '').replace(',', '')
    product_name = product_name_element.text.strip()
    
    return {
        'name': product_name,
        'price': float(price)
    }
