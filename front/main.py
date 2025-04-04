import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import pickle
from datetime import datetime
import requests

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Painéis Solares",
    page_icon="☀️",
    layout="wide"
)

# Título e descrição
st.title("☀️ Calculadora de Painéis Solares")
st.markdown("Calcule quantos painéis solares você precisa com base no seu consumo de energia e localização.")

try:
    irradiacao_por_regiao = requests.get("http://localhost:8000/geracao_por_regiao")
    irradiacao_por_regiao = irradiacao_por_regiao.json()
    print(irradiacao_por_regiao)
except Exception as e:
    irradiacao_por_regiao = {
        "Norte": 5.5,
        "Nordeste": 5.9,
        "Centro-Oeste": 5.7,
        "Sudeste": 5.5,
        "Sul": 5.0
    }

# Criar layout com colunas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Dados de Entrada")
    
    # Criar tabs para básico e avançado
    tab1, tab2 = st.tabs(["Cálculo Básico", "Opções Avançadas"])
    
    with tab1:
        # Consumo mensal
        consumo_mensal = st.number_input(
            "Consumo Mensal de Energia (kWh)",
            min_value=1.0,
            max_value=10000.0,
            value=300.0,
            step=10.0,
            help="Você pode encontrar essa informação na sua conta de luz"
        )
        
        # Região
        regiao = st.selectbox(
            "Região",
            options=list(irradiacao_por_regiao.keys()),
            index=3,  # Sudeste como padrão
            help="A região afeta a quantidade de irradiação solar disponível"
        )
        
        # Mostrar irradiação da região selecionada
        st.info(f"Irradiação solar média na região {regiao}: {irradiacao_por_regiao[regiao]} kWh/m²/dia")
    
    with tab2:
        # Potência do painel
        potencia_painel = st.slider(
            "Potência do Painel Solar (W)",
            min_value=250,
            max_value=550,
            value=400,
            step=10,
            help="Painéis mais potentes ocupam menos espaço, mas podem ser mais caros"
        )
        
        # Fator de performance
        fator_performance = st.slider(
            "Fator de Performance do Sistema",
            min_value=0.70,
            max_value=0.85,
            value=0.75,
            step=0.01,
            help="Considera perdas por temperatura, sujeira, cabeamento, etc."
        )
        
        # Preço médio do kWh
        preco_kwh = st.number_input(
            "Preço médio do kWh (R$)",
            min_value=0.1,
            max_value=2.0,
            value=0.75,
            step=0.01,
            help="Preço médio do kWh na sua região para calcular economia"
        )
        
        # Custo médio por Wp instalado
        custo_wp = st.number_input(
            "Custo médio por Wp instalado (R$)",
            min_value=3.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Custo médio por Watt-pico instalado (inclui painéis, inversor, estrutura, instalação)"
        )

# Botão de calcular
if st.button("Calcular Painéis Necessários", type="primary", use_container_width=True):
    # Obter irradiação da região selecionada
    irradiacao_media = irradiacao_por_regiao[regiao]
    
    # Cálculos
    energia_por_painel_mes = (potencia_painel / 1000) * irradiacao_media * 30 * fator_performance
    numero_paineis = math.ceil(consumo_mensal / energia_por_painel_mes)
    area_estimada = numero_paineis * (potencia_painel / 200)  # ~2m² por painel de 400W
    potencia_sistema = (numero_paineis * potencia_painel) / 1000  # kWp
    geracao_mensal = energia_por_painel_mes * numero_paineis
    
    # Cálculos financeiros
    custo_estimado = potencia_sistema * 1000 * custo_wp
    economia_mensal = geracao_mensal * preco_kwh
    tempo_retorno = custo_estimado / (economia_mensal * 12)  # em anos
    
    # Exibir resultados
    with col2:
        st.subheader("Resultados da Estimativa")
        
        # Criar métricas em grid
        col_a, col_b = st.columns(2)
        col_c, col_d = st.columns(2)
        
        with col_a:
            st.metric("Número de Painéis", f"{numero_paineis}")
        
        with col_b:
            st.metric("Potência do Sistema", f"{potencia_sistema:.2f} kWp")
        
        with col_c:
            st.metric("Área Estimada", f"{area_estimada:.1f} m²")
        
        with col_d:
            st.metric("Geração Mensal", f"{geracao_mensal:.0f} kWh")
        
        # Informações financeiras
        st.subheader("Análise Financeira")
        
        col_e, col_f, col_g = st.columns(3)
        
        with col_e:
            st.metric("Investimento Estimado", f"R$ {custo_estimado:.2f}")
        
        with col_f:
            st.metric("Economia Mensal", f"R$ {economia_mensal:.2f}")
        
        with col_g:
            st.metric("Tempo de Retorno", f"{tempo_retorno:.1f} anos")
        
        # Gráfico de geração vs consumo
        st.subheader("Geração vs Consumo")
        
        # Criar dados para o gráfico
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        # Variação sazonal simulada (fator multiplicador por mês)
        variacao_sazonal = {
            "Norte": [0.9, 0.85, 0.8, 0.85, 0.95, 1.05, 1.1, 1.15, 1.1, 1.05, 1.0, 0.95],
            "Nordeste": [1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.85, 0.9, 1.0, 1.05, 1.1, 1.1],
            "Centro-Oeste": [1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15],
            "Sudeste": [1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15],
            "Sul": [1.15, 1.1, 1.05, 1.0, 0.9, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1]
        }
        
        # Calcular geração mensal com variação sazonal
        geracao_por_mes = [geracao_mensal * fator for fator in variacao_sazonal[regiao]]
        consumo_por_mes = [consumo_mensal] * 12
        
        # Criar DataFrame
        df = pd.DataFrame({
            'Mês': meses,
            'Geração (kWh)': geracao_por_mes,
            'Consumo (kWh)': consumo_por_mes
        })
        
        # Plotar gráfico
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df['Mês'], df['Geração (kWh)'], color='#4CAF50', alpha=0.7, label='Geração Estimada')
        ax.plot(df['Mês'], df['Consumo (kWh)'], color='#F44336', marker='o', linewidth=2, label='Consumo')
        
        ax.set_xlabel('Mês')
        ax.set_ylabel('Energia (kWh)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        st.pyplot(fig)
        
        # Informações adicionais
        st.info("""
        **Informações importantes:**
        - A geração de energia varia conforme as estações do ano e condições climáticas
        - O tempo de retorno do investimento considera apenas a economia na conta de luz
        - A vida útil média dos painéis solares é de 25 anos
        """)
        
        st.warning("""
        Esta é uma estimativa baseada em médias. Para um dimensionamento preciso, 
        consulte um profissional especializado em energia solar.
        """)

# Adicionar informações extras na barra lateral
with st.sidebar:
    st.header("Sobre a Calculadora")
    st.markdown("""
    Esta calculadora fornece uma estimativa do número de painéis solares 
    necessários com base no seu consumo de energia e localização.
    
    **Como funciona:**
    1. Insira seu consumo mensal de energia
    2. Selecione sua região
    3. Ajuste as opções avançadas (opcional)
    4. Clique em "Calcular Painéis Necessários"
    
    **Fatores considerados:**
    - Irradiação solar média da região
    - Eficiência do sistema fotovoltaico
    - Potência dos painéis solares
    - Variação sazonal da geração
    """)
    
    st.header("Irradiação Solar por Região")
    
    # Criar DataFrame para a tabela
    df_irradiacao = pd.DataFrame({
        'Região': list(irradiacao_por_regiao.keys()),
        'Irradiação (kWh/m²/dia)': list(irradiacao_por_regiao.values())
    })
    
    st.dataframe(df_irradiacao, hide_index=True, use_container_width=True)
    
    # Adicionar mapa de calor simples
    st.subheader("Mapa de Irradiação Solar")
    
    # Dados para o mapa de calor (simplificado)
    regioes = list(irradiacao_por_regiao.keys())
    valores = list(irradiacao_por_regiao.values())
    
    # Normalizar valores para cores
    valores_norm = [(v - min(valores)) / (max(valores) - min(valores)) for v in valores]
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(8, 3))
    
    # Criar barras horizontais coloridas
    for i, (regiao, valor, valor_norm) in enumerate(zip(regioes, valores, valores_norm)):
        color = plt.cm.YlOrRd(valor_norm)
        ax.barh(regiao, valor, color=color)
        ax.text(valor + 0.05, i, f"{valor} kWh/m²/dia", va='center')
    
    ax.set_xlim(4.5, 6.5)
    ax.set_title("Irradiação Solar Média por Região")
    ax.set_xlabel("kWh/m²/dia")
    
    st.pyplot(fig)

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido com Streamlit e Python | Calculadora de Painéis Solares")