from pydantic import BaseModel,EmailStr
from typing import Optional
from starlette.requests import Request
from datetime import datetime

class users(BaseModel):
    username : str
    email : EmailStr
    password : str
    is_actice : bool = True



class login(BaseModel):
    email : EmailStr
    password : str
    
class tokendata(BaseModel):
    id : Optional[str] = None

class token(BaseModel) :
    access_token : str
    token_type : str

class update_users(BaseModel):
    username : str
    email : str
    is_staff : bool

class add(BaseModel):
    orders_id : str = None
    item_id : str
    item_name : str
    units_sold : int = 1
    unit_price : float
    total_prices : float = None
    orders_status : str = "unpaid"
    
class new_transactions(BaseModel):
    order_id : str = None
    id_customer : str = None
    payment_methods : str 
    order_status : str = 'Processing'
    order_date : datetime = None
    total_prices : float = None
    note : str 
        
    	
# 	id_customer varchar(50) NOT NULL,
# 	orders_id varchar(50) NOT NULL,
# 	item_id varchar(50) NOT NULL,
# 	item_name varchar(300) NOT NULL,
# 	units_sold int4 NOT NULL,
# 	unit_price numeric(10) NOT NULL,
# 	total_prices numeric(10) NOT NULL,
# 	orders_status varchar(50) NULL DEFAULT NULL::character varying,
# 	create_at timestamptz NULL DEFAULT CURRENT_TIMESTAMP
# );

# class update_order(BaseModel):
#     pizza_size: str
#     flavour: str
#     quantity: int
# class Order_view(BaseModel):
#     order_id : int
#     user_id : int
#     quantity: int
#     order_status : Optional[str] = None
#     pizza_size: str
#     flavour: str
#     create_at : str



# class update_order(Order):
#     pass
# class update_order_status(BaseModel):
#     orders_status : str