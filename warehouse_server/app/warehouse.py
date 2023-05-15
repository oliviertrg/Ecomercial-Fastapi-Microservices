from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import es
from fastapi.encoders import jsonable_encoder
from app import auth2,auth2_users
import requests
import json
from datetime import datetime

router = APIRouter (
    prefix = "/merchandise",
    tags = ["merchandise"]
)

es = es()

@router.post('/import',status_code=status.HTTP_201_CREATED)
async def import_merchandise(request: Request,current_user : int = Depends(auth2.get_current_user)):
 try:
     body = await request.json()
     user = {"users_id_who_created" : int(current_user.id),
             'timestamp': datetime.now()}
     body.update(user)
     print(body)
     resp = es.index(index="grocery_store", document=body)
     
 except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{e}")
     
 return {"id_product":resp['_id'],
         "status":resp['result']}



@router.put('/update_product/{product_id}',status_code=status.HTTP_200_OK)
async def update_product(product_id : str,request: Request ,current_user : int = Depends(auth2.get_current_user)):
    try:
     body = await request.json()
     user = {"users_id_who_created" : int(current_user.id)}
     body.update(user)
     print(body)
     resp = es.index(index="grocery_store",id=product_id,document=body)

    except Exception as ex:
     print(f"Error {ex}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{ex}")

    
     
    return {
            "id_product":resp['_id'],
            "status":resp['result']
            }
@router.delete('/delete/{product_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(product_id : str,current_user : int = Depends(auth2.get_current_user)):
  try:
    resp = es.delete(index="grocery_store", id=product_id) 
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  
  return Response(status_code=status.HTTP_204_NO_CONTENT)



# @router.get('/views=id/{product_id}')
# async def view_orders(product_id : str,current_user : int = (Depends(auth2.get_current_user),Depends(auth2_users.get_current_user))):
#   try:
#     resp = es.search(index="grocery_store", id=product_id) 
#   except Exception as e:
#      print(f"Error {e}")
#      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                          detail="CAN'T FIND ANY PRODUCTS ")
#   return resp 

@router.get('/views/{search_query}')
async def view_orders(search_query : str,current_user : int = (Depends(auth2.get_current_user),Depends(auth2_users.get_current_user))):
  try:
    r = list()
    ree = es.search(index="grocery_store",query={"multi_match": {"query": search_query,
                                                                 "fields":["product","type","_id"]}})
    if len(ree['hits']['hits']) == 0 :
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
    for i in ree['hits']['hits']:
     r.append(i["_source"]) 
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return r

@router.get('/views/all')
async def view_orders(search_query : str,current_user : int = (Depends(auth2.get_current_user),Depends(auth2_users.get_current_user))):
  try:
    r = list()
    ree = es.search(index="grocery_store", query={"match_all": {}})
    if len(ree['hits']['hits']) == 0 :
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
    for i in ree['hits']['hits']:
     r.append(i["_source"]) 
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return r




    
# @router.get('/views')
# async def view_orders(current_user : int = Depends(auth2.get_current_user)):
    
#     sql = f'''select order_id,orders.user_id,order_status,flavour,pizza_size,quantity,orders.create_at  
#               from "orders" left join "users" on orders.user_id = users.user_id 
#               where orders.user_id = {int(current_user.id)} ;'''
#     c.execute(sql)
#     view  = c.fetchall()
#     model_view = list()
#     if len(view) == 0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"you dont have any order")
#     else:
#         for i in view :
#          model_view.append(jsonable_encoder({
#                             "order_id" : i[0],
#                             "user_name":i[1],
#                             "order_status":i[2],
#                             "flavour":i[3],
#                             "pizza_size":i[4],
#                             "quantity":i[5],
#                             "create_at":i[6]
#                            }))
#     return model_view
            




