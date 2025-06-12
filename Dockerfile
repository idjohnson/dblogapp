FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DB_HOST=pg-295c4a9c-isaac-1040.aivencloud.com
ENV DB_PORT=11996
ENV DB_NAME=defaultdb
ENV DB_USER=avnadmin
ENV DB_PASS=xxx
ENV DB_SSLMODE=require

EXPOSE 5000

CMD ["python", "app.py"]
