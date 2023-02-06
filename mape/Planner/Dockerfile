FROM python:3.10
VOLUME "/tmp"
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pandas
RUN pip install influxdb-client
RUN pip install numpy
RUN pip install scipy
RUN pip --default-timeout=1000 install  statsmodels
RUN pip install scipy
RUN pip install Flask
RUN pip install jsonify
RUN pip install python-dotenv
RUN pip install requests
COPY . .
CMD ["python", "-u", "buy_sell_planning.py"]



