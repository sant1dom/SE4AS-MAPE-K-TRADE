FROM python:3.10
VOLUME "/tmp"
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install requests
RUN pip install influxdb-client
RUN pip install pandas
COPY . .
CMD ["python", "-u", "update_v2.py"]
#CMD ["python", "-u", "monitor.py"]