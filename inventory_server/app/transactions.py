from fastapi import FastAPI,Request ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import curso
# from fastapi.encoders import jsonable_encoder
from app import auth2_admin,schema ,auth2
import requests
import json
from datetime import datetime
from fastapi.middleware.cors import  CORSMiddleware
router = APIRouter (
    prefix = "/transactions",
    tags = ["transactions"]
)

@router.get('/views/id_customer={id_customer}')
async def view_all(id_customer : int,current_users : int = (Depends(auth2.get_current_user),Depends(auth2_admin.get_current_user))):
  try: 
    
    
    db = curso()
    c = db.cursor()
    sql = f"""select * from transactions where id_customer = {id_customer}"""
    c.execute(sql)
    z = c.fetchall()
    x = list()
    for i in z :
     t = schema.history(
       order_id = i[0] ,
       id_customer = i[1] ,
       payment_methods = i[2] ,
       order_status = i[3] ,
       order_date = str(i[4]) ,
       ship_date = str(i[5]) ,
       total_prices = float(i[6]) ,
       note = i[7]
     )
     x.append(t.dict())  
     
    l = schema.List(__root__ = x)
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return l
# @router.put('/update_status/{order_id}')
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

@router.get('/views/orders_id=?{orders_id}')
async def view_all(orders_id : str, current_users : int = (Depends(auth2_admin.get_current_user))):
  try:
    db = curso()
    c = db.cursor()
    sql = f"""select * from transactions where orders_id = '{orders_id}'"""
    c.execute(sql)
    z = c.fetchall()
     
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return z

# @router.post('/orders/')
# async def create_transactions(new_transactions : schema.new_transactions,order_id : str,current_user : int = Depends(auth2_admin.get_current_user)):
#    db = curso()
#    c = db.cursor()
#    try:
#     s = (new_transactions.order_id,new_transactions.id_customer,
#          new_transactions.payment_methods,new_transactions.order_status, 
#          new_transactions.total_prices,new_transactions.note)
#     sqll = '''insert into transactions(orders_id,id_customer,payment_methods,order_status,
#               total_prices,note)
#               values(%s,%s,%s,%s,%s,%s) ;
#               '''
#     c.execute(sqll,s)
#     db.commit()
#     new_transactions.order_date = datetime.now()
   
    
#    except Exception as e:
#      print(f"Error {e}")
#      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                          detail=f"{e}") 
#    return new_transactions

@router.delete('/delete-orders/{order_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id : str,current_admin : int = Depends(auth2_admin.get_current_user)):
    db = curso()
    c = db.cursor()
    sql = f"""select * from "transactions" where id_customer = '{int(current_admin.id)}'
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
        sql1 = f"""delete from "transactions" where id_customer = '{int(current_admin.id)}'
                                          and"orders_id" = '{order_id}' 
                                          and order_status = 'Processing';"""
        c.execute(sql1)
        db.commit()
  