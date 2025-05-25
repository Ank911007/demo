# Dockerfile
FROM python:3.10

WORKDIR /app
COPY backend/ /app/
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y unzip terraform

EXPOSE 5000
CMD ["python", "backend.py"]
