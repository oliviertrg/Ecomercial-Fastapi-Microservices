from pydantic import BaseModel,EmailStr
from typing import Optional
from starlette.requests import Request


class users(BaseModel):
    username : str
    email : EmailStr
    password : str
    is_actice : bool = True
    is_staff : bool  = False

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

# class Order(BaseModel):
#     pizza_size : str
#     flavour : str
#     quantity : int
#     orders_status : str = "pending"

# class update_order(Order):
#     pass
# class update_order_status(BaseModel):
#     orders_status : str