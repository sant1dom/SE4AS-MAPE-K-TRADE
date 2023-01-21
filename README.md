# SE4AS-MAPE-K-TRADE
 MAPE-K Trading bot using Docker and Binance API
 To run the bot, you need to have Docker installed on your machine and Docker Compose.\
 Then run the following commands:
 ```bash
    docker-compose build
    docker-compose up
 ```
 The bot will start by downloading the data of the specifed coins and then start trading. \
 You need to specify the token for InfluxDB in the code for now (will be changed in the future).
