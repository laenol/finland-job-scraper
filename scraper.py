import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = [
    "Sustainability Specialist", 
    "ICT Project Manager",
    "Robotics Engineer",
    "Sustainability Consultant",
    "ESG Manager",
    "R&D Engineer IT",
    "Digitalization Lead",
    "Automation Specialist"
]

def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(api_url, json=payload)
    except:
        pass

def scrape_jobs(keyword):
    encoded_query = urllib.parse.quote(keyword)
    url = f"https://duunitori.fi/tyopaikat?haku={encoded_query}&alue=Suomi&sort=newest"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_jobs = []
        cards = soup.select('div[class*="job-box"]')
        
        for card in cards[:3]:
            try:
                title_el = card.find('h3')
                if not title_el:
                    continue
                
                title = title_el.text.strip()
                
                if any(x in title.lower() for x in ["doctoral", "professor", "lecturer", "postdoc"]):
                    continue
                    
                company_el = card.find('span', class_='job-box__company')
                company = company_el.text.strip() if company_el else "Private Company"
                
                link_el = card.find('a')
                link = "https://duunitori.fi" + link_el['href'] if link_el else "#"
                
                found_jobs.append(f"🏢 <b>{company}</b>\n🛠 <b>{title}</b>\n🔗 <a href='{link}'>Apply Here</a>")
            except:
                continue
        return found_jobs
    except:
        return []

def main():
    final_report = []
    for kw in KEYWORDS:
        results = scrape_jobs(kw)
        if results:
            final_report.append(f"🔍 <b>Matches for '{kw}':</b>\n" + "\n\n".join(results))
    
    if final_report:
        header = "🏭 <b>New Industrial Job Matches (Finland):</b>\n\n"
        full_msg = header + "\n\n---\n\n".join(final_report)
        
        if len(full_msg) > 4000:
            parts = [full_msg[i:i+4000] for i in range(0, len(full_msg), 4000)]
            for part in parts:
                send_telegram(part)
        else:
            send_telegram(full_msg)

if __name__ == "__main__":
    main()
