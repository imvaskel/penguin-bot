FROM python:3.9.4-slim-buster
LABEL maintainer="vaskel <contact@vaskel.xyz>"
RUN apt update && apt-get install gcc git -y && pip install --upgrade pip setuptools wheel 
WORKDIR /src/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]