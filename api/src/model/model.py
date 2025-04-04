import pickle
import pandas as pd
import numpy as np
from datetime import datetime   

def carregar_modelo():
    """
    Carrega o modelo de radiação solar e as informações das features
    
    Returns:
        tuple: (modelo, feature_info)
    """
    # Carregar o modelo
    with open('/app/src/model/modelo_radiacao_solar.pkl', 'rb') as f:
        modelo = pickle.load(f)
    
    # Carregar informações das features
    with open('/app/src/model/features_info.pkl', 'rb') as f:
        feature_info = pickle.load(f)
    
    return modelo, feature_info

def calcular_media_diaria(latitude, longitude, data=None, altitude=500):
    """
    Calcula a média diária de radiação solar para uma localização específica
    
    Args:
        latitude: Latitude em graus decimais (string ou float)
        longitude: Longitude em graus decimais (string ou float)
        data: Data específica (string 'YYYY-MM-DD' ou objeto datetime)
        altitude: Altitude em metros
        
    Returns:
        float: Média diária de radiação solar em kWh/m²
    """
    # Carregar o modelo
    modelo, _ = carregar_modelo()
    
    # Se não foi fornecida uma data, usar a data atual
    if data is None:
        data = datetime.now().date()
    elif isinstance(data, str):
        data = datetime.strptime(data, '%Y-%m-%d').date()
    
    # Extrair componentes temporais
    ano = data.year
    mes = data.month
    dia = data.day
    dia_ano = data.timetuple().tm_yday
    
    # Criar features cíclicas
    mes_sen = np.sin(2 * np.pi * mes / 12)
    mes_cos = np.cos(2 * np.pi * mes / 12)
    dia_ano_sen = np.sin(2 * np.pi * dia_ano / 365)
    dia_ano_cos = np.cos(2 * np.pi * dia_ano / 365)
    
    # Converter latitude e longitude para float se forem strings
    if isinstance(latitude, str):
        latitude = float(latitude.replace(',', '.'))
    if isinstance(longitude, str):
        longitude = float(longitude.replace(',', '.'))
    
    # Resultados para diferentes horas do dia
    resultados = []
    
    # Prever para cada hora do dia (das 6h às 18h)
    for hora in range(6, 19):
        # Criar features cíclicas para hora
        hora_sen = np.sin(2 * np.pi * hora / 24)
        hora_cos = np.cos(2 * np.pi * hora / 24)
        
        # Definir valores meteorológicos médios para o mês
        if mes >= 4 and mes <= 9:  # Meses mais frios no hemisfério sul
            temperatura = 20
            precipitacao = 0
            umidade = 60
        else:  # Meses mais quentes no hemisfério sul
            temperatura = 28
            precipitacao = 5
            umidade = 75
        
        # Criar dados para previsão
        dados = {
            'latitude': [latitude],
            'longitude': [longitude],
            'altitude': [altitude],
            'mes': [mes],
            'dia_ano': [dia_ano],
            'hora': [hora],
            'mes_sen': [mes_sen],
            'mes_cos': [mes_cos],
            'hora_sen': [hora_sen],
            'hora_cos': [hora_cos],
            'dia_ano_sen': [dia_ano_sen],
            'dia_ano_cos': [dia_ano_cos],
            'temperatura_do_ar___bulbo_seco_horaria_degc': [temperatura],
            'precipitacao_total_horario_mm': [precipitacao],
            'umidade_relativa_do_ar_horaria_percent': [umidade],
            'vento_velocidade_horaria_m_s': [2.0],  # Valor médio
        }
        
        # Criar DataFrame
        df_previsao = pd.DataFrame(dados)
        
        # Adicionar features derivadas que o modelo espera
        # Distância do equador (valor absoluto da latitude)
        df_previsao['dist_equador'] = np.abs(latitude)
        
        # Interação latitude-mês (captura variação sazonal por latitude)
        df_previsao['lat_mes_interact'] = latitude * np.cos(2 * np.pi * mes / 12)
        
        # Declinação solar (aproximada)
        declinacao = 23.45 * np.sin(np.radians(360/365 * (dia_ano - 81)))
        df_previsao['declinacao_solar'] = declinacao
        
        # Elevação solar aproximada ao meio-dia
        elevacao_solar = 90 - np.abs(latitude - declinacao)
        df_previsao['elevacao_solar_approx'] = elevacao_solar
        
        # Interação latitude-hora
        df_previsao['lat_hora_interact'] = latitude * np.sin(np.pi * hora / 12)
        
        # Lista de features que o modelo espera
        features = [
            'latitude', 'longitude', 'altitude',
            'mes', 'dia_ano', 'hora',
            'mes_sen', 'mes_cos', 
            'hora_sen', 'hora_cos',
            'dia_ano_sen', 'dia_ano_cos',
            'temperatura_do_ar___bulbo_seco_horaria_degc',
            'precipitacao_total_horario_mm',
            'umidade_relativa_do_ar_horaria_percent',
            'vento_velocidade_horaria_m_s',
            'dist_equador', 'lat_mes_interact', 'declinacao_solar', 
            'elevacao_solar_approx', 'lat_hora_interact'
        ]
        
        # Filtrar apenas as features que existem
        features_existentes = [f for f in features if f in df_previsao.columns]
        
        # Fazer previsão
        radiacao = modelo.predict(df_previsao[features_existentes])[0]
        resultados.append(radiacao)
    
    # Calcular média das horas diurnas e converter de kJ/m² para kWh/m²
    # 1 kWh/m² = 3600 kJ/m²
    media_diaria_kwh = sum(resultados) / len(resultados) / 3.6 / 365 * 2.8
    
    return media_diaria_kwh 


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
