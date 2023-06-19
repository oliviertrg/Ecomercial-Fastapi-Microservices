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


from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

app = FastAPI()


@cache()
async def get_cache():
    return 1


@app.get("/")
@cache(expire=60)
async def index():
    return dict(hello="world")


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")