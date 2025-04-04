from model import calcular_media_diaria
import json
from datetime import datetime
import numpy as np
import pandas as pd

# Dados de coordenadas por região
irradiacao_por_regiao = {
    "Norte": {"latitude": -3.4653, "longitude": -62.2159},       # Próximo a Manaus (AM)
    "Nordeste": {"latitude": -8.0476, "longitude": -34.8770},    # Próximo a Recife (PE)
    "Centro-Oeste": {"latitude": -15.7801, "longitude": -47.9292}, # Brasília (DF)
    "Sudeste": {"latitude": -23.5505, "longitude": -46.6333},    # São Paulo (SP)
    "Sul": {"latitude": -30.0346, "longitude": -51.2177}         # Porto Alegre (RS)
}

def calcular_media_diaria_por_regiao():
    """
    Calcula a média diária de radiação solar para cada região do Brasil
    
    Returns:
        dict: Dicionário com médias diárias de radiação solar por região em kWh/m²/dia
    """
    resultado = {}
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    for regiao, coords in irradiacao_por_regiao.items():
        latitude = coords["latitude"]
        longitude = coords["longitude"]
        
        # Calcular média diária para hoje
        media_diaria = calcular_media_diaria(latitude, longitude, data=hoje)
        
        # Converter para float Python nativo e arredondar
        media_diaria = round(float(media_diaria), 2)
        
        # Armazenar apenas o valor da média diária
        resultado[regiao] = media_diaria
    
    return resultado

# Calcular médias diárias por região
medias_diarias = calcular_media_diaria_por_regiao()

# Imprimir apenas os valores de média diária por região
print(medias_diarias)
