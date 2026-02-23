import requests
from bs4 import BeautifulSoup
import os

# 1. Setup
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://duunitori.fi/tyopaikat?haku=IT&alue=Suomi&sort=newest"

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(api_url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

def scrape_jobs():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find job boxes (Duunitori uses 'job-box' class)
    job_cards = soup.find_all('div', class_='job-box')
    
    new_jobs = []
    for card in job_cards[:5]: # Just look at the 5 newest
        title = card.find('h3').text.strip()
        link = "https://duunitori.fi" + card.find('a')['href']
        company = card.find('span', class_='job-box__company').text.strip()
        
        job_info = f"<b>{title}</b>\n🏢 {company}\n🔗 {link}"
        new_jobs.append(job_info)
    
    if new_jobs:
        send_telegram("🚀 <b>New IT Jobs in Finland:</b>\n\n" + "\n\n".join(new_jobs))
    else:
        print("No jobs found today.")

if __name__ == "__main__":
    scrape_jobs()