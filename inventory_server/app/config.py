import psycopg2
from elasticsearch import Elasticsearch
from datetime import datetime
# 1. Import the config object from decouple.
from decouple import config


def curso():
 try :
    conn = psycopg2.connect(
        host = 'host.docker.internal',
        port=54323,
        database = config('POSTGRES_DB'),
        user = config('POSTGRES_USER'),
        password = config('POSTGRES_PASSWORD')
    )
    print("conecting susseccefull")

 except Exception as e :
    print("-"*200)
    print("Connecting to database failed")
    print(f"Error {e}" )
 return conn

def es():
 try :
  es = Elasticsearch(
        "http://host.docker.internal:9200",
        basic_auth=(config("ELASTIC_USER"),
                config("ELASTIC_PASSWORD"))
    )
  print("conecting susseccefull")
 except Exception as e :
    print("-"*200)
    print("Connecting to database failed")
    print(f"Error {e}" )
 return es

if __name__ == "__main__":
         curso()
         es()