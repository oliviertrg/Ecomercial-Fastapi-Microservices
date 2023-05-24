from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import es
from fastapi.encoders import jsonable_encoder
from app import auth2
from app import schema
import requests
import json
from datetime import datetime

router = APIRouter (
    prefix = "/cart",
    tags = ["cart"]
)
@router.post('/',status_code=status.HTTP_201_CREATED)
async def create_order(new_order : schema.add,current_user : int = Depends(auth2.get_current_user)):
 try:
     # not create customer id yet
     sql = '''insert into cart(id_customer,orders_id,item_id,item_name,units_sold,
              unit_price,total_prices,orders_status)
              values(%s,%s,%s,%s,%s,%s,%s,%s) ;
              select order_id from orders order by create_at desc limit 1 ;
              '''
     x = (int(current_user.id),new_order.orders_id,new_order.item_id,new_order.item_name,new_order.units_sold,
              new_order.unit_price,(new_order.unit_price*new_order.units_sold),new_order.orders_status)
     c.execute(sql,x)
     y = c.fetchall()
     db.commit()
 except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{e}")
     
 return new_order



@router.put('/update_order_status/{order_id}')
async def update_order_status(order_id : int,order_status : update_order_status ,current_user : int = Depends(auth2.get_current_user)):

    sql = f'''select * from "orders"
              where "order_id" = {order_id} ; '''
    sql2 = f'''select * from "users" 
               where "user_id" = {int(current_user.id)}; '''
    c.execute(sql)
    y = c.fetchall()
    if len(y) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with id: {order_id} does not exist")
    c.execute(sql2)
    x = c.fetchall()
    if x[0][5] == False :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
       try:
        sql1 = f'''UPDATE "orders" SET 
                          order_status = '{order_status.orders_status}' 
                          WHERE order_id = {order_id};'''
        c.execute(sql1)
        db.commit()
        
        body = {
           "pizza_size" : y[0][2] ,
           "flavour" : y[0][3],
           "quantity" : y[0][4] 
        }
        
        req = requests.get('http://host.docker.internal:8000/ingredient/' ,json=body)
        d = (json.dumps(req.json()).encode("utf-8"))
        
        producer.send(ORDER_KAFKA_TOPIC,d) 
       except Exception as e :
         print(f"Error {e}")
         raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              detail = f"{e}")
    #    print("body : ",body)
    #    print("d : ",d)  
       return order_status

@router.get('/views')
async def view_orders(current_user : int = Depends(auth2.get_current_user)):
    
    sql = f'''select order_id,orders.user_id,order_status,flavour,pizza_size,quantity,orders.create_at  
              from "orders" left join "users" on orders.user_id = users.user_id 
              where orders.user_id = {int(current_user.id)} ;'''
    c.execute(sql)
    view  = c.fetchall()
    model_view = list()
    if len(view) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"you dont have any order")
    else:
        for i in view :
         model_view.append(jsonable_encoder({
                            "order_id" : i[0],
                            "user_name":i[1],
                            "order_status":i[2],
                            "flavour":i[3],
                            "pizza_size":i[4],
                            "quantity":i[5],
                            "create_at":i[6]
                           }))
    return model_view
            


@router.put('/update/{order_id}',response_model=update_order)
async def update_order(order_id : int,new_order : update_order,current_user : int = Depends(auth2.get_current_user)) :

    sql = f'''select * from "orders" where "order_id" = {order_id} ; '''
    c.execute(sql)
    x = c.fetchall()
    if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with id: {order_id} does not exist")
    if x[0][1] != int(current_user.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
     try:
        sql1 = f'''UPDATE "orders" SET 
                  pizza_size = (%s) ,
                  flavour = (%s) ,
                  quantity = (%s)
                  WHERE order_id = {order_id};'''
        x = (new_order.pizza_size,new_order.flavour,new_order.quantity)
        c.execute(sql1,x)
        db.commit()
     except Exception as e:
         print(f"Error {e}")
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail=f"{e}")
         
     return new_order


@router.delete('/delete/{order_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id : int,current_user : int = Depends(auth2.get_current_user)):

    sql = f'''select * from "orders" where "order_id" = {order_id} ; '''
    c.execute(sql)
    x = c.fetchall()
    if len(x) == 0 :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"order with id: {order_id} does not exist")
    if x[0][1] != int(current_user.id) :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
        sql1 = f'''delete from "orders" where "order_id" = {order_id} ;'''
        c.execute(sql1)
        db.commit()
    print("newupdate")



