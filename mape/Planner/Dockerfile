FROM python:3.10
VOLUME "/tmp"
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install requests
RUN pip install Flask
RUN pip install jsonify

COPY . .
CMD ["python", "-u", "buy_sell_planning.py"]



