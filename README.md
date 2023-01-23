# SE4AS-MAPE-K-TRADE
 MAPE-K Trading bot using Docker and Binance API
 To run the bot, you need to have Docker installed on your machine and Docker Compose.\
 Then run the following commands:
 ```bash
    docker-compose build
    docker-compose up
 ```
 The bot will start by downloading the data of the specifed coins and then start trading. \
 In order to manage variables needed for the monitor you need to create a file called .env in the root directory of the project. \
 Ex:
 ```bash
     INFLUXDB_TOKEN=<token>
     INFLUXDB_ORG=<your-org>
     INFLUXDB_BUCKET=<your-bucket>
     INFLUXDB_URL=http://<name-of-your-influxdb-container>:8086
  ```

