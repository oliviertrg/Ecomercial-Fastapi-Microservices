# a = {"a" : 1,
#      "b" : 2,
#      "c" : 3}
# # print(a)

# # if "d" not in a:
# #     print(a["b"])
# # else:
# #     print("dosen't exist")    

# # if "c" not in a:
# #      raise a["a"]
# # else:
# #      print("dosen't exist")

# try :
#     try:
#         if "d" not in a:
#             print("something")
#             raise Exception("0")  # 1
#         else:
#             print("dosen't exist")
#     except :
#             print("testing")
  
     
# except :
#     print("erro")    

# a = list()
# for i in range(1,9):
#     a.append(list())
#     for j in range(1,11) :
#         a[i-1].append(j*(i+1))
# print(a)
# for i in a:
#     print(i)


# a = [{"id" : "123","cart" : list()},{"id" : "1"},{"id" : "3"},{"id" : "2"}]
# b = {"id":"123","item":1}
# c = {"id":"123","item":2}
# print(a)
# for i in a:
#     if i["id"] == b["id"] :

#         i["cart"].append(b)
#         i["cart"].append(c)

#     else:
#         print("wrong")
# print(a)
# x = {"cart":[{"id":1},{"id":2}]}


# from fastapi import FastAPI
# from starlette.requests import Request
# from starlette.responses import Response

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache

# from redis import asyncio as aioredis

# app = FastAPI()


# @cache()
# async def get_cache():
#     return 1


# @app.get("/")
# @cache(expire=60)
# async def index():
#     return dict(hello="world")


# @app.on_event("startup")
# async def startup():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
# def loc():
#     a = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG1pbnNfaWQiOjEsImV4cCI6MTY4NzAyNDUyN30.vCcwPcvNVq7OHejiiTa3LuNxXbsJ8fHIENsr9uRubT8"

#     b = list()

#     for i in a:
#         b.append(i)
#     return b
# def ham_an(x):
#     return x[1]

# def dem():
#     x = set(loc())
#     z = list()
#     q = 0
#     for i in x:
#        t = loc().count(i)
#        z.append([])
#        z[q].append(i)
#        z[q].append(t)
#        q += 1
#     z.sort(key=ham_an,reverse=True)   
#     return z

# for i in dem():
#     print(i)

# from kafka import KafkaConsumer
# import json
# from config import curso

# ORDER_KAFKA_TOPIC = "cart_details"

# ORDER_CONFIRMED_KAFKA_TOPIC = "update_order_status_confirmed"


# consumer = KafkaConsumer(
#                         ORDER_KAFKA_TOPIC,
#                         bootstrap_servers=['host.docker.internal:9300'],
#                         api_version=(0,11,5)
#                         )

# def kafka_event():
#   print("sending ","="*200,">>>>>>>>>>>>>>>>>>>>>>")
#   try: 
#     db = curso()
#     c = db.cursor()
#     for i in consumer:
#        b = json.loads(i[6].decode())
#        sqll = f"""
#                            UPDATE inventory SET 
#                            quantity = quantity - {int(b["units_sold"])}
#                           where item_id = '{b["item_id"]}'

#               """
#        c.execute(sqll)
#        db.commit()
#        print(f" confirm quantity of <{b['item_id']}> check was send ","="*50,">>>>>>")
#   except Exception as e:
#       print(f"Error {e}")  

# if __name__ == "__main__":
#   kafka_event()

