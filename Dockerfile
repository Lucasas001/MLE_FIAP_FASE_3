FROM python:3.12-slim

ENV POETRY_VERSION=2.1.1
ENV PYTHONPATH="/app/src"

RUN apt-get update && \
    apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock* README.md entrypoint.sh ./

COPY ./api/src/ src/

RUN poetry config virtualenvs.create false \
    && poetry self add poetry-plugin-export \
    && poetry install --no-interaction --no-ansi \
    && rm -rf ~/.cache

EXPOSE 8080 8501

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]