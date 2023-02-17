import pandas as pd
from influxdb_client import InfluxDBClient, QueryApi
import os
import statsmodels.api as sm
import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify
#rimetter influx invece di localhost
def get_ml_result(coin):
  load_dotenv()

  INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
  INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
  INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
  INFLUXDB_URL = os.getenv("INFLUXDB_URL")

  app = Flask(__name__)

  client = InfluxDBClient(url="http://localhost:8086", token=INFLUXDB_TOKEN, org=INFLUXDB_ORG, timeout=30_000)

  query_api = client.query_api()
  query = f'from(bucket: "crypto")\
    |> range(start: -1y)\
    |> filter(fn: (r) => r["_measurement"] == "{coin.upper()}USDT")'
  result = query_api.query(org=INFLUXDB_ORG, query=query)

  results = []
  for table in result:
    for record in table.records:
      results.append((record.get_field(), record.get_value(),record.get_time()))
      
  data=pd.DataFrame(results)
  data=data.rename({0:"_field",1:"_value",2:"_time"},axis=1)
  data['_time'] = pd.to_datetime(data['_time'],format='%Y-%m-%dT%H:%M:%SZ',errors='coerce')
  data['_value']=pd.to_numeric(data['_value'],errors='coerce',downcast="float")
  data.dropna(inplace=True)
  data=pd.pivot(data,index='_time',columns='_field',values='_value')
  data=data.reset_index()
  data
  exog=data.copy()
  exog.drop('high',axis=1,inplace=True)

  exog['_time']=pd.DatetimeIndex(exog.reset_index()['_time']) + pd.DateOffset(hours=1)
  data=data[1:]
  last_exog=exog.iloc[-1]
  exog=exog.iloc[:-1]

  data.set_index('_time',inplace=True)
  exog.set_index('_time',inplace=True)

  endog=data['high'].values.reshape(-1,1)
  model = sm.tsa.arima.ARIMA(endog=endog[:-1],exog=np.array(exog[:-1],dtype='float'), order=(5,3,3))
  results = model.fit(method='statespace')
  result=results.forecast(steps=1,exog=exog.iloc[-1])
  result=result[0]
  return result

print(get_ml_result("ETH"))