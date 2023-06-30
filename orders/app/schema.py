from pydantic import BaseModel,EmailStr
from typing import Optional,List
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
    access_token : Optional[str] = None
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
    units_sold : int = 0
    unit_price : float
    total_prices : float = None
    orders_status : str = "unpaid"

class items(BaseModel):
     __root__: List[add]    
  
    
class new_transactions(BaseModel):
    order_id : str = None
    id_customer : str = None
    payment_methods : str 
    order_status : str = 'Processing'
    order_date : datetime = None
    total_prices : float = None
    note : str 
        
class update_cart(BaseModel):
    item_id : str 
    units_sold : int = 0	
