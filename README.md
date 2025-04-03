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