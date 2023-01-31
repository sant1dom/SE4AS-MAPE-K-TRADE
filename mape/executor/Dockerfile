FROM python:3.10
VOLUME "/tmp"
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pyalgotrade
COPY . .
#CMD ["python", "-u", "executor.py"]