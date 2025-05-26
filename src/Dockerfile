FROM python:3.9.6

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y libgl1 && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 4000
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000", "--debug"]