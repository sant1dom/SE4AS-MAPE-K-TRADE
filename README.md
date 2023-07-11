# SE4AS-MAPE-K-TRADE
> Project developed for the Software Engineering for Autonomous System course - University of L'Aquila

This repository contains the implementation of **MAPE-K Trading Bot**: Project developed for the Software Engineering for Autonomous System course - University of L'Aquila

## Installation Requirements
1. Install the latest version of Docker - https://docs.docker.com/get-docker/
2. Install the latest version of Docker Compose (if not already installed) - https://docs.docker.com/compose/install/

## Project Description

This project consists in a set of containers running in Docker and automatically configured using the file *docker-compose.yml*. In the following the description of them:

 - **MAPE-K-Loop / Managing System containers**
	 - *MAPE_MONITOR*: The monitor has been realized using <a href="https://requests.readthedocs.io/en/latest/">Python Requests Module</a>. It gets the data from the <a href="https://www.binance.com/en/binance-api">Binance API<a> and stores it in the knowledge (InfluxDB)  
	 - *MAPE_PLANNER*: The planner has been realized using statsmodels(<a href="https://www.statsmodels.org/stable/index.html">) and Flask <a href="https://flask.palletsprojects.com/en/2.3.x/">. 
	 - *MAPE_EXECUTOR*: The executor works using Flask(<a href="https://flask.palletsprojects.com/en/2.3.x/">) and <a href="https://requests.readthedocs.io/en/latest/">Python Requests.
	 - *KNOWLEDGE*: The knowledge of the loop has been realized using InfluxDB (https://www.influxdata.com), 
 - **Other services containers**
	 - *grafana_container*: A dashboard that allows us to graphically monitor the system and check if it is working properly.
## Configuration
The configuration of the system is mainly contained in the *docker-compose.yml* file. Be sure that all the exposed mapped ports are free on your environment:
- **3005** for the Monitor
- **3001** for the Executor
- **5020** for the Planner
- **8086** for InfluxDB
- **3000** for the Grafana dashboard

If you are not able to free all the listed ports, you can change the mapping in the compose file.

In order to manage variables needed for the monitor you need to create a file called .env in the root directory of the project. \
 Ex:
 ```bash
INFLUXDB_TOKEN=<token>
INFLUXDB_ORG=<your-org>
INFLUXDB_BUCKET=<your-bucket>
INFLUXDB_URL=http://<name-of-your-influxdb-container>:8086
  ```
an example of working .env file is the following
```bash
INFLUXDB_TOKEN=my-super-secret-auth-token
INFLUXDB_ORG=se4as
INFLUXDB_BUCKET=crypto
INFLUXDB_URL=http://influx:8086
```


## Running 
First of all you have to open your terminal on this folder and build all the images running the following command:
```bash
    docker-compose build
```
Then, you can run all the containers with the following command:
```bash
    docker-compose up -d
```
The bot will start by downloading the data of the specified coins and then start trading.
If you want to stop all, you can use this:
```bash
    docker-compose down
```
    
 
## Authors
This project has been realized by:
- Domenico Santone (<a href="https://github.com/sant1dom">GitHub Page</a>)
- Dario Di Mambro (<a href="https://github.com/ddm18">GitHub Page</a>)
- Alberto Isotti (<a href="https://github.com/albertoisotti">GitHub Page</a>)


