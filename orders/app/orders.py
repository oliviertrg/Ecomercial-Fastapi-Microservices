from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
from app import auth2,auth2_admin,schema
import requests
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend
import json
from datetime import datetime
from app.config import curso
import uuid
import random
import string
from kafka import KafkaProducer
import numpy as np

ORDER_KAFKA_TOPIC = "transactions_details"

producer = KafkaProducer(bootstrap_servers=['host.docker.internal:9300'],
                         api_version=(0,11,5))
  

router = APIRouter ()

@router.get('/query={search_query}')
async def view(search_query : str):
  try:
    req = await requests.get(f'http://host.docker.internal:9100/merchandise/views/query={search_query}')
    j = (req.json())
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return j




def redis_cache():
    return caches.get(CACHE_KEY)
@router.get('/history/')
async def historys(current_user : int = Depends(auth2.get_current_user),cache: RedisCacheBackend = Depends(redis_cache)):
  try: 
    db = curso()
    my_headers = {'Authorization' : f'Bearer {current_user.access_token}'}
    response = await requests.get(f'http://host.docker.internal:9100/transactions/views/id_customer={current_user.id}', headers=my_headers)
    h = response.json()
    sql = f"""select * from cart where id_customer = {current_user.id}"""
    a =  db.prepare(sql)
    x = np.array(a())

    for i in h :
      if i['order_id'] in x[:,1]:
        rows = np.where(x[:,1] == i['order_id'])
        result = [{'order_id':j[1],'item_id':j[2],'item_name' : j[3],
                   'units_sold' : j[4],'unit_price' : float(j[5]),
                   'total_prices' : float(j[6]),'orders_status' : j[7] } for j in x[rows] ]
        
        i["cart"] = result    
        

  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

  return h


@router.get('/cart/views/orders_id={orders_id}')
async def historys(orders_id : str,current_users : int = (Depends(auth2.get_current_user),Depends(auth2_admin.get_current_user)),cache : RedisCacheBackend = Depends(redis_cache)):
  try: 
    db = curso()
    c = db.cursor()
    sql = f"""select * from cart where orders_id = '{orders_id}'"""
    c.execute(sql)
    x = c.fetchall()
    y = list()
    for i in x :
     t = schema.add(
          orders_id = i[1] ,
          item_id  = i[2] ,
          item_name = i[3] ,
          units_sold = i[4] ,
          unit_price = float(i[5])  ,
          total_prices = float(i[6]) ,
          orders_status = i[7]
       ).dict()
     y.append(t)  
     
    l = schema.items(__root__ = y)
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action") 
  return l

@router.post('/cart/',status_code=status.HTTP_201_CREATED)
async def create_order(new_order : schema.add,current_user : int = Depends(auth2.get_current_user)):
 
 try:
    db = curso()
    c = db.cursor()
    sql = f'''select orders_id,orders_status from cart where id_customer = '{int(current_user.id)}'
              order by create_at desc limit 1 ''' 
    c.execute(sql)
    check = c.fetchall()
    if len(check) == 0 or check[0][1] == 'paid':  
        a = True
        while  a :
            u = uuid.uuid1()
            i = f'{str(u.hex)}'.join(random.sample(string.ascii_lowercase,2))  
            sql = f"""select * from cart where orders_id = '{i}'"""
            c.execute(sql)
            z = c.fetchall()
            if len(z) == 0:
                a = False
                orders_id = i

    elif check[0][1] == 'unpaid' :
       orders_id  = check[0][0]            

    new_order.orders_id = orders_id
    new_order.total_prices=float(new_order.unit_price*new_order.units_sold) 
    
    sql = '''insert into cart(id_customer,orders_id,item_id,item_name,units_sold,
              unit_price,total_prices,orders_status)
              values(%s,%s,%s,%s,%s,%s,%s,%s) ;
              '''
    x = (int(current_user.id),orders_id,new_order.item_id,new_order.item_name,new_order.units_sold,
              new_order.unit_price,new_order.total_prices,new_order.orders_status)
    c.execute(sql,x)
    db.commit()
 except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{e}")
     
 return new_order

@router.put('/update-cart/')
async def create_order(update : schema.update_cart,current_user : int = Depends(auth2.get_current_user)):

    db = curso()
    c = db.cursor()
    sql = f"""select * from "cart" where id_customer = '{int(current_user.id)}' and orders_status = 'unpaid' ; """
    c.execute(sql)
    x = c.fetchall()
    if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with users {int(current_user.id)} does not exist")
    elif x[0][0] != int(current_user.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
      try:      
        sql1 = f"""update cart set units_sold = {update.units_sold}
              where item_id = '{update.item_id}' ;"""
        c.execute(sql1)
        db.commit()
      except Exception as e:
         print(f"Error {e}")
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                 detail="Not authorized to perform requested action")
    return update

@router.delete('/delete-items/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(item_id : int,current_user : int = Depends(auth2.get_current_user)):
   
    db = curso()
    c = db.cursor()
    sql = f"""select * from "cart" where id_customer = '{int(current_user.id)}' and orders_status = 'unpaid' ; """
    c.execute(sql)
    x = c.fetchall()
    if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with users {int(current_user.id)} does not exist")
    elif x[0][0] != int(current_user.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
      try:      
        sql1 = f"""delete from "cart" where id_customer = '{int(current_user.id)}'
                                      and orders_status = 'unpaid'  
                                      and "item_id" = '{item_id}';"""
        c.execute(sql1)
        db.commit()
      except Exception as e:
         print(f"Error {e}")
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                 detail="Not authorized to perform requested action")
    return Response(status_code=status.HTTP_204_NO_CONTENT)  
      
      
@router.post('/transactions/{order_id}')
async def create_transactions(new_transactions : schema.new_transactions,order_id : str,current_user : int = Depends(auth2.get_current_user)):
   try:
    db = curso()
    c = db.cursor()
    sql = f"""select sum(total_prices) from cart
              where orders_id = '{order_id}'
              group by orders_id ;
              """
    sql2 = f"""select distinct orders_status from cart where orders_id = '{order_id}' ;"""
    c.execute(sql)
    y = c.fetchall()
    c.execute(sql2)
    x = c.fetchall()
    new_transactions.order_id=order_id
    new_transactions.id_customer=str(current_user.id)
    new_transactions.total_prices=float(y[0][0])
    
   except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
   if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with users {int(current_user.id)} does not exist")
   if x[0][0] == 'unpaid':
      body = new_transactions.dict()    
      d = (json.dumps(body).encode("utf-8"))
      producer.send(ORDER_KAFKA_TOPIC,d)
      sql3 = f""" update cart set orders_status = 'paid'
              where orders_id = '{order_id}'; """
      c.execute(sql3)
      db.commit()
   
   else:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"YOUR ORDERS ({new_transactions.order_id}) ALREADY PAID SO YOU CANT DO IT AGAIN")   
   new_transactions.order_date = datetime.now()
    
   return new_transactions




