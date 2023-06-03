from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
# from app.config import es
from fastapi.encoders import jsonable_encoder
from app import auth2
from app import schema
import requests
import json
from datetime import datetime
from app.config import curso
import uuid
import random
import string
router = APIRouter ()
# @router.get('/query=*')
# async def view_all():
#   try:
#     r = list()
#     ree = es.search(index="grocery_store", query={"match_all": {}})
#     if len(ree['hits']['hits']) == 0 :
#       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                          detail="CAN'T FIND ANY PRODUCTS ")
#     for i in ree['hits']['hits']:
#      r.append(i["_source"]) 
#   except Exception as e:
#      print(f"Error {e}")
#      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                          detail="CAN'T FIND ANY PRODUCTS ")
#   return r
@router.get('/query={search_query}')
async def view(search_query : str):
  try:
    req = requests.get(f'http://host.docker.internal:9100/merchandise/views/query={search_query}')
    d = (json.dumps(req.json()).encode("utf-8"))
    j = (req.json())
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
   
  return j
@router.post('/cart/',status_code=status.HTTP_201_CREATED)
def create_order(new_order : schema.add,current_user : int = Depends(auth2.get_current_user)):
 db = curso()
 c = db.cursor()
 try:
    sql = f'''select orders_id,orders_status from cart where id_customer = '{int(current_user.id)}'
              order by create_at desc limit 1 ''' 

    c.execute(sql)
    check = c.fetchall()
    if len(check) == 0 or check[0][1] == 'paid':  
        a = True
        while  a :
            u = uuid.uuid1()
            i = f'{str(u.hex)}'.join(random.sample(string.ascii_lowercase,4))  
            sql = f"""select * from cart where orders_id = '{i}'"""
            c.execute(sql)
            z = c.fetchall()
            if len(z) == 0:
                a = False
                orders_id = i

    elif check[0][1] == 'unpaid' :
       orders_id  = check[0][0]            
    
     # not create customer id yet
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

@router.delete('/delete-items/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(item_id : int,current_user : int = Depends(auth2.get_current_user)):
    db = curso()
    c = db.cursor()
    sql = f"""select * from "cart" where id_customer = '{int(current_user.id)}' and orders_status = 'unpaid' ; """
    c.execute(sql)
    x = c.fetchall()
    print(x)
    if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with users {int(current_user.id)} does not exist")
    elif x[0][0] != int(current_user.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
        sql1 = f"""delete from "cart" where id_customer = '{int(current_user.id)}'
                                      and orders_status = 'unpaid'  
                                      and "item_id" = '{item_id}';"""
        c.execute(sql1)
        db.commit()



# @router.post('/transactions/{order_id}',response_model = schema.receipt)
@router.post('/transactions/{order_id}')
async def create_transactions(new_transactions : schema.new_transactions,order_id : str,current_user : int = Depends(auth2.get_current_user)):
   db = curso()
   c = db.cursor()
   try:
    sql = f"""update cart set orders_status = 'paid'
              where orders_id = '{order_id}';

              select sum(total_prices) from cart
              where orders_id = '{order_id}'
              group by orders_id ;"""
    c.execute(sql)
    y = c.fetchall()
    s = (order_id,int(current_user.id),new_transactions.payment_methods,
         new_transactions.order_status,float(y[0][0]),new_transactions.note)
    sqll = '''insert into transactions(orders_id,id_customer,payment_methods,order_status,
              total_prices,note)
              values(%s,%s,%s,%s,%s,%s) ;
              '''
    c.execute(sqll,s)
    db.commit()
    new_transactions.order_id=order_id
    new_transactions.id_customer=str(current_user.id)
    new_transactions.order_date = datetime.now()
    new_transactions.total_prices=float(y[0][0])
    
   except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{e}") 
   return new_transactions

@router.delete('/delete-orders/{order_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id : str,current_user : int = Depends(auth2.get_current_user)):
    db = curso()
    c = db.cursor()
    sql = f"""select * from "transactions" where id_customer = '{int(current_user.id)}'
                                          and"orders_id" = '{order_id}' 
                                          and order_status = 'Processing' ; """
    c.execute(sql)
    x = c.fetchall()

    if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with id: {order_id} does not exist")
    if x[0][1] != int(current_user.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
        sql1 = f"""delete from "transactions" where id_customer = '{int(current_user.id)}'
                                          and"orders_id" = '{order_id}' 
                                          and order_status = 'Processing';"""
        c.execute(sql1)
        db.commit()
  
    
    # if len(y) == 0:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"order with id: {order_id} does not exist")
    # c.execute(sql2)
    # x = c.fetchall()
    # if x[0][5] == False :
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorized to perform requested action")
    # else:
    #    try:
    #     sql1 = f'''UPDATE "orders" SET 
    #                       order_status = '{order_status.orders_status}' 
    #                       WHERE order_id = {order_id};'''
    #     c.execute(sql1)
    #     db.commit()
        
    #     body = {
    #        "pizza_size" : y[0][2] ,
    #        "flavour" : y[0][3],
    #        "quantity" : y[0][4] 
    #     }
        
    #     req = requests.get('http://host.docker.internal:8000/ingredient/' ,json=body)
    #     d = (json.dumps(req.json()).encode("utf-8"))
        
    #     producer.send(ORDER_KAFKA_TOPIC,d) 
    #    except Exception as e :
    #      print(f"Error {e}")
    #      raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                           detail = f"{e}")
    #    print("body : ",body)
    #    print("d : ",d)  
    

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

# @router.put('/update_order_status/{order_id}')
# async def update_order_status(order_id : int,order_status : update_order_status ,current_user : int = Depends(auth2.get_current_user)):

#     sql = f'''select * from "orders"
#               where "order_id" = {order_id} ; '''
#     sql2 = f'''select * from "users" 
#                where "user_id" = {int(current_user.id)}; '''
#     c.execute(sql)
#     y = c.fetchall()
#     if len(y) == 0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"order with id: {order_id} does not exist")
#     c.execute(sql2)
#     x = c.fetchall()
#     if x[0][5] == False :
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="Not authorized to perform requested action")
#     else:
#        try:
#         sql1 = f'''UPDATE "orders" SET 
#                           order_status = '{order_status.orders_status}' 
#                           WHERE order_id = {order_id};'''
#         c.execute(sql1)
#         db.commit()
        
#         body = {
#            "pizza_size" : y[0][2] ,
#            "flavour" : y[0][3],
#            "quantity" : y[0][4] 
#         }
        
#         req = requests.get('http://host.docker.internal:8000/ingredient/' ,json=body)
#         d = (json.dumps(req.json()).encode("utf-8"))
        
#         producer.send(ORDER_KAFKA_TOPIC,d) 
#        except Exception as e :
#          print(f"Error {e}")
#          raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                               detail = f"{e}")
#     #    print("body : ",body)
#     #    print("d : ",d)  
#        return order_status

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
            


# @router.put('/update/{order_id}',response_model=update_order)
# async def update_order(order_id : int,new_order : update_order,current_user : int = Depends(auth2.get_current_user)) :

#     sql = f'''select * from "orders" where "order_id" = {order_id} ; '''
#     c.execute(sql)
#     x = c.fetchall()
#     if len(x) == 0 :
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"order with id: {order_id} does not exist")
#     if x[0][1] != int(current_user.id) :
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="Not authorized to perform requested action")
#     else:
#      try:
#         sql1 = f'''UPDATE "orders" SET 
#                   pizza_size = (%s) ,
#                   flavour = (%s) ,
#                   quantity = (%s)
#                   WHERE order_id = {order_id};'''
#         x = (new_order.pizza_size,new_order.flavour,new_order.quantity)
#         c.execute(sql1,x)
#         db.commit()
#      except Exception as e:
#          print(f"Error {e}")
#          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                              detail=f"{e}")
         
#      return new_order


# @router.delete('/delete/{order_id}',status_code=status.HTTP_204_NO_CONTENT)
# async def delete_order(order_id : int,current_user : int = Depends(auth2.get_current_user)):

#     sql = f'''select * from "orders" where "order_id" = {order_id} ; '''
#     c.execute(sql)
#     x = c.fetchall()
#     if len(x) == 0 :
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"order with id: {order_id} does not exist")
#     if x[0][1] != int(current_user.id) :
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="Not authorized to perform requested action")
#     else:
#         sql1 = f'''delete from "orders" where "order_id" = {order_id} ;'''
#         c.execute(sql1)
#         db.commit()
#     print("newupdate")



