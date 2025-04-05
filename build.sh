docker build -t model_api .
docker run -d --name model_api -p 8080:8080 -p 8501:8501 model_api
docker tag model_api:latest us-central1-docker.pkg.dev/theta-style-455822-r3/app/model_api:latest
docker push us-central1-docker.pkg.dev/theta-style-455822-r3/app/model_api:latest
