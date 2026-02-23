import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = [
    "Summer Trainee Robotics",
    "Automaatio harjoittelija",
    "Junior Automation Engineer",
    "Robotiikka kesätyö",
    "Trainee Software Engineering",
    "Junior Robotics Engineer",
    "Summer Trainee IT"
]

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        requests.post(api_url, json=payload, timeout=10)
    except:
        pass

def scrape_jobs():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    seen_links = set()
    final_results = []

    for kw in KEYWORDS:
        encoded_query = urllib.parse.quote(kw)
        url = f"https://duunitori.fi/tyopaikat?haku={encoded_query}&alue=Suomi&sort=newest"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.select('div.job-box, a.job-box')
            
            kw_matches = []
            for card in cards[:5]:
                link_tag = card if card.name == 'a' else card.find('a')
                if not link_tag or not link_tag.get('href'):
                    continue
                
                full_link = "https://duunitori.fi" + link_tag['href']
                if full_link in seen_links:
                    continue
                
                title_tag = card.find('h3')
                title = title_tag.text.strip() if title_tag else "New Opening"
                
                if any(x in title.lower() for x in ["senior", "lead", "architect", "manager", "professor"]):
                    continue

                company_tag = card.find('span', class_='job-box__company')
                company = company_tag.text.strip() if company_tag else "Check listing"
                
                seen_links.add(full_link)
                kw_matches.append(f"🤖 <b>{title}</b>\n🏢 {company}\n🔗 <a href='{full_link}'>View Posting</a>")
            
            if kw_matches:
                final_results.append(f"🔍 <b>Results for: {kw}</b>\n" + "\n\n".join(kw_matches))
                
        except:
            continue

    if final_results:
        report = "⚡ <b>Daily Robotics/Automation Feed (BSc Level)</b>\n\n" + "\n\n---\n\n".join(final_results)
        for i in range(0, len(report), 4000):
            send_telegram(report[i:i+4000])

if __name__ == "__main__":
    scrape_jobs()
