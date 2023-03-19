FROM python:3.10
VOLUME "/tmp"
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install requests
RUN pip install influxdb_client
COPY . .
CMD ["python", "-u", "executor.py"]