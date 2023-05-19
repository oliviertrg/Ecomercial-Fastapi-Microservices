from fastapi import FastAPI , status ,HTTPException,APIRouter
from app import users,auth,auth_users
from fastapi.middleware.cors import  CORSMiddleware
from starlette.requests import Request

from users.app import orders



app = FastAPI()

origins = ["http://0.0.0.0:6969/"]

app.add_middleware(
    CORSMiddleware ,
    allow_origins = origins ,
    allow_credentials = True ,
    allow_methods = ["*"] ,
    allow_headers = ["*"]
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(auth_users.router)
app.include_router(orders.router)
@app.get("/test")
async def test():
    return {"testing":"done"}


