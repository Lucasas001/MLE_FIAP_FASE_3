import shutil
import requests
from src.core.config import USER_AGENT

def download_file(url: str, destination: str) -> bool:
    """
    Baixa um arquivo a partir da URL e salva no destino especificado.
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(destination, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return True
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return False