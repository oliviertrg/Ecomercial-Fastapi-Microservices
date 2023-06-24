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
class history(BaseModel):
    order_id : str 
    id_customer : str 
    payment_methods : str
    order_status : str
    order_date : str 
    ship_date : str 
    total_prices : float 
    note : str 
    cart : list = list()
class List(BaseModel):
     __root__: List[history]    
        
class update_order_status(BaseModel):
     orders_status : str

