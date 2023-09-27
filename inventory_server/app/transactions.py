from fastapi import FastAPI,Request ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import curso
# from fastapi.encoders import jsonable_encoder
from app import auth2_admin,schema ,auth2
import requests
import json
from datetime import datetime
from kafka import KafkaProducer

ORDER_KAFKA_TOPIC = "cart_details"

producer = KafkaProducer(bootstrap_servers=['host.docker.internal:9300'],
                         api_version=(0,11,5))
  
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
@router.put('/update_order_status/{order_id}')
async def historys(order_id:str,order_status:schema.update_order_status,current_users : int = Depends(auth2_admin.get_current_user)):

    db = curso()
    c = db.cursor()
    sql = f"""select * from transactions
              where orders_id = '{order_id}' ; """

    c.execute(sql)
    y = c.fetchall()
    
    if len(y) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with id: {order_id} does not exist")
    if y[0][3] == 'delivered' :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="ALREADY SENT THE UPDATE STATUS CONFIRM ")
    else:
     try:
        sql1 = f"""UPDATE transactions SET 
                          order_status = '{order_status.orders_status}' ,
                          ship_date = NOW() 
                          WHERE orders_id = '{order_id}';"""
        c.execute(sql1)
        db.commit()
        my_headers = {'Authorization' : f'Bearer {current_users.access_token}'}
        response = await requests.get(f'http://host.docker.internal:6969/cart/views/orders_id={order_id}', headers=my_headers)
        h = response.json()
        for i in h :
         d = (json.dumps(i).encode("utf-8"))
         producer.send(ORDER_KAFKA_TOPIC,d)
         
    
  
     except Exception as e:
       print(f"Error {e}")
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    return order_status

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
    if x[0][1] != int(current_admin.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
        sql1 = f"""delete from "transactions" where id_customer = '{int(current_admin.id)}'
                                          and"orders_id" = '{order_id}' 
                                          and order_status = 'Processing';"""
        c.execute(sql1)
        db.commit()
  