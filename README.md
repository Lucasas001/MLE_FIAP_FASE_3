Projeto de API com Poetry

Este projeto é uma API simples gerenciada com [Poetry](https://python-poetry.org/), usando Python 3.13.

## Como rodar

1. **Instale as dependências com o Poetry:**

```bash
poetry install
```

2. **Inicie a API:**

```bash
poetry run uvicorn src.api.main:app --reload    
```

3. **Acesse a documentação interativa:**

```bash
http://localhost:8000/docs
```

## Estrutura do Projeto

```bash
src/
├── api/
│ ├── __init__.py
│ ├── main.py
│ └── models.py
└── tests/
```

## Notebook de Estudo

O notebook principal com a análise completa e desenvolvimento do modelo está disponível em:

[Notebook de Estudo](estudo/main.ipynb)


## Considerações Finais

Neste estudo, desenvolvemos um modelo de previsão de radiação solar utilizando dados meteorológicos históricos do INMET.

Principais pontos do trabalho:

1. **Coleta e Preparação de Dados**: Processamos dados meteorológicos de diferentes estações, tratando valores ausentes e normalizando variáveis.

2. **Análise Exploratória**: Identificamos padrões sazonais na radiação solar e correlações com outras variáveis meteorológicas como temperatura e umidade.

3. **Engenharia de Features**: Criamos variáveis cíclicas para representar adequadamente o tempo (hora, dia, mês) e incorporamos informações geográficas.

4. **Modelagem**: Implementamos um modelo de aprendizado de máquina que consegue prever a radiação solar com base em múltiplas variáveis.

5. **Comparação Regional**: Analisamos as diferenças nos padrões de radiação solar entre regiões distintas do Brasil, destacando a influência da latitude.

6. **Limitações**: O modelo atual pode ser aprimorado com dados de mais estações e variáveis adicionais como nebulosidade e aerossóis atmosféricos.

7. **Aplicações Potenciais**: Este modelo pode ser utilizado para dimensionamento de sistemas fotovoltaicos, planejamento agrícola e estudos climáticos.

Próximos passos incluem a implementação de modelos mais complexos como redes neurais e a integração com dados de satélite para melhorar a precisão das previsões.


## Deploy do Modelo e Aplicação Web

O modelo desenvolvido neste estudo foi implementado em produção no GCP e está disponível através de:

1. **Aplicação Web**: Uma calculadora de painéis solares que permite dimensionar sistemas fotovoltaicos com base nas previsões do modelo.
   - **URL**: [http://34.44.229.246:8501/](http://34.44.229.246:8501/)

2. **API REST**: Um endpoint que fornece previsões de radiação solar para todas as regiões do Brasil.
   - **URL**: [http://34.44.229.246:8080/model/](http://34.44.229.246:8080/model/)

Sinta-se à vontade para acessar e utilizar estas ferramentas.
