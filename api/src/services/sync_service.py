import re
import requests
from bs4 import BeautifulSoup
from src.core.config import INMET_URL, USER_AGENT

def get_download_links() -> dict:
    """
    Realiza o scraping do portal INMET e retorna os anos disponíveis e os links de download.
    Retorna um dicionário com 'available_years' e 'download_links'.
    """
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(INMET_URL, headers=headers)
    if response.status_code != 200:
        raise Exception("Erro ao acessar o portal do INMET.")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    available_years = []
    download_links = {}
    
    for link in soup.find_all('a'):
        href = link.get('href', '')
        text = link.text.strip()
        
        year = None
        year_match_href = re.search(r'(\d{4})\.zip', href)
        year_match_text = re.search(r'ANO\s+(\d{4})', text)
        
        if year_match_href:
            year = year_match_href.group(1)
        elif year_match_text:
            year = year_match_text.group(1)
        
        if year:
            if href.startswith('/'):
                full_link = f"https://portal.inmet.gov.br{href}"
            elif not href.startswith('http'):
                full_link = f"https://portal.inmet.gov.br/{href}"
            else:
                full_link = href
            
            download_links[year] = full_link
            if year not in available_years:
                available_years.append(year)
    
    available_years.sort()
    return {"available_years": available_years, "download_links": download_links}