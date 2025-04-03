import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.services.sync_service import get_download_links
from src.services.download_service import download_all_files
from src.core.config import DOWNLOAD_DIR
from geopy.geocoders import Nominatim

router = APIRouter()
geolocator = Nominatim(user_agent="mle_tech_challenge_three")

@router.get("/geocode/{address}")
async def geocode_address(address: str = None):
    """
    Recebe um endereço como parâmetro e retorna a latitude e longitude.
    """
    location = geolocator.geocode(address)
    if location:
        return {"latitude": location.latitude, "longitude": location.longitude}
    else:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")

@router.get("/health", tags=["Status"])
async def health_check():
    """
    Endpoint para verificar o status da API.
    """
    return {"status": "ok"}

@router.get("/sync_data", tags=["Sync Data"])
async def sync_data():
    """
    Endpoint para obter a lista de anos e links de download disponíveis.
    """
    try:
        data = get_download_links()
        return {"status": "ok", **data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download_data", tags=["Download Data"])
async def download_data(background_tasks: BackgroundTasks, years: list[str] = None):
    """
    Endpoint para iniciar o download dos arquivos.
    Se 'years' não for especificado, baixa todos os anos disponíveis.
    """
    background_tasks.add_task(download_all_files, years)
    return {
        "status": "ok",
        "message": "Download iniciado em segundo plano",
        "years": years if years else "todos os anos disponíveis"
    }

@router.get("/download_status", tags=["Download Data"])
async def download_status():
    """
    Endpoint para verificar o status dos arquivos baixados.
    """
    if not DOWNLOAD_DIR.exists():
        return {"status": "ok", "files": []}
    
    files = []
    for file in os.listdir(DOWNLOAD_DIR):
        if file.endswith('.zip'):
            file_path = DOWNLOAD_DIR / file
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