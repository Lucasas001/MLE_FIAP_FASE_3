import os
from src.core.config import DOWNLOAD_DIR
from src.utils.file_utils import download_file
from src.services.sync_service import get_download_links

def download_all_files(years: list[str] = None) -> dict:
    """
    Realiza o download dos arquivos dos anos especificados.
    Se 'years' for None, baixa todos os anos disponíveis.
    Retorna um dicionário com os resultados do download.
    """
    data = get_download_links()
    available_years = data["available_years"]
    download_links = data["download_links"]
    
    if years:
        years_to_download = [year for year in years if year in available_years]
    else:
        years_to_download = available_years
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    results = {}
    for year in years_to_download:
        url = download_links.get(year)
        if url:
            file_path = DOWNLOAD_DIR / f"{year}.zip"
            success = download_file(url, str(file_path))
            results[year] = {
                "success": success,
                "file_path": str(file_path) if success else None
            }
    return results