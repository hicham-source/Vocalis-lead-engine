import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse, urljoin
import re

def is_allowed_by_robots(url):
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(base_url, "robots.txt"))
        rp.read()
        return rp.can_fetch("*", url)
    except:
        return True

def extract_contact_info(url):
    if not url or not is_allowed_by_robots(url):
        return None, None, None, None
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        html_content = str(soup)
        
        wa_match = re.search(r'(?:wa\.me/|api\.whatsapp\.com/send\?phone=)(\d+)', html_content)
        whatsapp = wa_match.group(1) if wa_match else None
        
        email_match = re.search(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', html_content)
        email = email_match.group(1) if email_match else None
        
        ig_match = re.search(r'href="(https?://(?:www\.)?instagram\.com/[^"]+)"', html_content)
        instagram = ig_match.group(1) if ig_match else None
        
        li_match = re.search(r'href="(https?://(?:www\.)?linkedin\.com/company/[^"]+)"', html_content)
        linkedin = li_match.group(1) if li_match else None
        
        return whatsapp, email, instagram, linkedin
    except Exception as e:
        return None, None, None, None

def enrich_leads():
    from database import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT place_id, website FROM leads WHERE whatsapp IS NULL AND email IS NULL AND website IS NOT NULL")
    leads = c.fetchall()
    
    for place_id, website in leads:
        wa, email, ig, li = extract_contact_info(website)
        c.execute('''
            UPDATE leads 
            SET whatsapp = ?, email = ?, instagram = ?, linkedin = ?
            WHERE place_id = ?
        ''', (wa, email, ig, li, place_id))
        
    conn.commit()
    conn.close()
    print(f"[Enrichment] Processed {len(leads)} websites.")
