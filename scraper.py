import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://duunitori.fi/tyopaikat?haku=IT&alue=Suomi&sort=newest"

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(api_url, json=payload)
    except Exception as e:
        print(f"Telegram failed: {e}")

def scrape_jobs():

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    job_cards = soup.select('div[class*="job-box"], a[class*="job-box"]')
    
    new_jobs = []
    for card in job_cards[:5]:
        try:
            title_el = card.find('h3')
            title = title_el.text.strip() if title_el else "Unknown Title"

            link_el = card.find('a') if card.name != 'a' else card
            link = "https://duunitori.fi" + link_el['href'] if link_el else "#"
            
            company_el = card.find('span', class_='job-box__company')
            company = company_el.text.strip() if company_el else "Company not listed"
            
            job_info = f"🚀 <b>{title}</b>\n🏢 {company}\n🔗 <a href='{link}'>View Job</a>"
            new_jobs.append(job_info)
        except Exception as e:
            print(f"Skipping a job listing because of an error: {e}")
            continue
    
    if new_jobs:
        message = "\n\n---\n\n".join(new_jobs)
        send_telegram(f"<b>New IT Jobs in Finland:</b>\n\n{message}")
    else:
        print("No jobs found with the current filters.")

if __name__ == "__main__":
    scrape_jobs()
