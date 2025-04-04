docker build -t model_api .
docker run -d --name model_api -p 8080:8080 -p 8501:8501 model_api