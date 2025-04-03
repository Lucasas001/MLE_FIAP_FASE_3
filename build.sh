docker build -t model_api .
docker run -d --name model_api -p 8080:8080 model_api