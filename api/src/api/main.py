from fastapi import FastAPI, HTTPException, BackgroundTasks
import os
import requests
from bs4 import BeautifulSoup
import re
import shutil
from pathlib import Path

app = FastAPI(
    title="API Simples",
    description="Uma API simples com endpoint de health check",
    version="0.1.0"
)

# Diretório para salvar os arquivos baixados
DOWNLOAD_DIR = Path("./downloads")

# Criar o diretório de downloads se não existir
DOWNLOAD_DIR.mkdir(exist_ok=True)

@app.get("/health", tags=["Status"])
async def health_check():
    """
    Endpoint para verificar o status da API.
    Retorna status 'ok' se a API estiver funcionando corretamente.
    """
    return {"status": "ok"}

@app.get("/sync_data", tags=["Sync Data"])
async def sync_data():
    """
    Endpoint para obter a lista de anos disponíveis e seus respectivos links de download.
    """
    # Baixar dados
    import requests
    from bs4 import BeautifulSoup
    import re

    url = "https://portal.inmet.gov.br/dadoshistoricos"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Imprimir o conteúdo HTML para debug
    print(f"Status code: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    # Armazenar anos e links
    available_years = []
    download_links = {}
    
    # Procurar por links que contenham texto como "ANO 2001" ou "2001.zip"
    for link in soup.find_all('a'):
        href = link.get('href', '')
        text = link.text.strip()
        
        # Verificar no href
        year_match_href = re.search(r'(\d{4})\.zip', href)
        # Verificar no texto
        year_match_text = re.search(r'ANO\s+(\d{4})', text)
        
        year = None
        if year_match_href:
            year = year_match_href.group(1)
            if href.startswith('/'):
                full_link = f"https://portal.inmet.gov.br{href}"
            elif not href.startswith('http'):
                full_link = f"https://portal.inmet.gov.br/{href}"
            else:
                full_link = href
            download_links[year] = full_link
        elif year_match_text:
            year = year_match_text.group(1)
            if href.startswith('/'):
                full_link = f"https://portal.inmet.gov.br{href}"
            elif not href.startswith('http'):
                full_link = f"https://portal.inmet.gov.br/{href}"
            else:
                full_link = href
            download_links[year] = full_link
        
        if year and year not in available_years:
            available_years.append(year)
    
    # Ordenar anos
    available_years = sorted(available_years)

    return {
        "status": "ok", 
        "available_years": available_years,
        "download_links": download_links
    }

def download_file(url, destination):
    """
    Função auxiliar para baixar um arquivo de uma URL e salvá-lo em um destino específico.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(destination, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return True
    except Exception as e:
        print(f"Erro ao baixar {url}: {str(e)}")
        return False

def download_all_files_task(years=None):
    """
    Tarefa em background para baixar todos os arquivos dos anos especificados.
    Se years for None, baixa todos os anos disponíveis.
    """
    # Obter os links de download
    data = sync_data()
    download_links = data["download_links"]
    available_years = data["available_years"]
    
    # Filtrar anos se especificados
    if years:
        years_to_download = [year for year in years if year in available_years]
    else:
        years_to_download = available_years
    
    # Criar diretório de downloads se não existir
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Baixar cada arquivo
    results = {}
    for year in years_to_download:
        if year in download_links:
            url = download_links[year]
            file_path = os.path.join(DOWNLOAD_DIR, f"{year}.zip")
            success = download_file(url, file_path)
            results[year] = {
                "success": success,
                "file_path": str(file_path) if success else None
            }
    
    return results

@app.post("/download_data", tags=["Download Data"])
async def download_data(background_tasks: BackgroundTasks, years: list[str] = None):
    """
    Endpoint para baixar os arquivos de dados dos anos especificados.
    Se nenhum ano for especificado, baixa todos os anos disponíveis.
    O download é executado em segundo plano.
    
    - **years**: Lista opcional de anos para baixar (ex: ["2001", "2002"])
    """
    # Adicionar tarefa em background
    background_tasks.add_task(download_all_files_task, years)
    
    return {
        "status": "ok",
        "message": "Download iniciado em segundo plano",
        "years": years if years else "todos os anos disponíveis"
    }

@app.get("/download_status", tags=["Download Data"])
async def download_status():
    """
    Endpoint para verificar o status dos downloads.
    Retorna a lista de arquivos baixados e seus tamanhos.
    """
    if not os.path.exists(DOWNLOAD_DIR):
        return {"status": "ok", "files": []}
    
    files = []
    for file in os.listdir(DOWNLOAD_DIR):
        if file.endswith('.zip'):
            file_path = os.path.join(DOWNLOAD_DIR, file)
            file_size = os.path.getsize(file_path)
            files.append({
                "name": file,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2)
            })
    
    return {
        "status": "ok",
        "download_directory": str(DOWNLOAD_DIR),
        "files": files
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)