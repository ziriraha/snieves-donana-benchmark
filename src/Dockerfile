FROM python:3.9.6

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y libgl1 && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# For megadetector
RUN git clone https://github.com/ultralytics/yolov5 && \
    pip install --no-cache-dir -r yolov5/requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/yolov5"

EXPOSE 4000
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000", "--debug"]