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
db = curso()
c = db.cursor()
@router.post('/cart/',status_code=status.HTTP_201_CREATED)
def create_order(new_order : schema.add,current_user : int = Depends(auth2.get_current_user)):
 try:
    sql = f'''select orders_id,orders_status from cart where id_customer = '{int(current_user.id)}'
              order by create_at desc limit 1 ''' 

    c.execute(sql)
    check = c.fetchall()
    print(check)
    if len(check) == 0 :  
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
    sql = '''insert into cart(id_customer,orders_id,item_id,item_name,units_sold,
              unit_price,total_prices,orders_status)
              values(%s,%s,%s,%s,%s,%s,%s,%s) ;
              '''
    x = (int(current_user.id),orders_id,new_order.item_id,new_order.item_name,new_order.units_sold,
              new_order.unit_price,float(new_order.unit_price*new_order.units_sold),new_order.orders_status)
    c.execute(sql,x)
    db.commit()
 except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{e}")
     
 return new_order

# @router.post('/transactions/{order_id}',response_model = schema.receipt)
@router.post('/transactions/{order_id}')
async def create_transactions(new_transactions : schema.new_transactions,order_id : str,current_user : int = Depends(auth2.get_current_user)):

    sql = f"""select sum(total_prices) from cart
              where orders_id = '{order_id}'
              group by orders_id ;"""
    # sql = f"""select * from cart
    #           where orders_id = '{order_id}'
    #           ;"""
    c.execute(sql)
    y = c.fetchall()
    print(y)
    s = (order_id,int(current_user.id),new_transactions.payment_methods,
         new_transactions.order_status,float(y[0][0]),new_transactions.note)
    sqll = '''insert into cart(orders_id,id_customer,payment_methods,order_status,
              total_prices,note)
              values(%s,%s,%s,%s,%s,%s) ;
              '''
    c.execute(sqll,s)
    db.commit()
    schema.receipt(order_id=order_id,id_customer=int(current_user.id),
                   payment_methods=new_transactions.payment_methods,
                   order_date = datetime.now(),total_prices=float(y[0][0]),
                   note = new_transactions.note)
    return schema.receipt

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



