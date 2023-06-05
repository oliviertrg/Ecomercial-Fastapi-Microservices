from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import curso
from fastapi.encoders import jsonable_encoder
from app import auth2_admin,schema 
import requests
import json
from datetime import datetime

router = APIRouter (
    prefix = "/transactions/",
    tags = ["transactions"]
)

@router.get('/views/query=?{orders_id}')
async def view_all(orders_id : str ):
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
async def delete_order(order_id : str,current_user : int = Depends(auth2_admin.get_current_user)):
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
  