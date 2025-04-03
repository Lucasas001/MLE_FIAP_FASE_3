import uvicorn
from fastapi import FastAPI
from src.api.endpoints import router as api_router

app = FastAPI(
    title="API Simples",
    description="API com endpoints para health check, sincronização e download de dados",
    version="0.1.0"
)

app.include_router(api_router)

# if __name__ == "__main__":  
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
