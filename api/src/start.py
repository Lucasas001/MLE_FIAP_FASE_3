import uvicorn

def main():
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)