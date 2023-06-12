from fastapi import FastAPI , status ,HTTPException,APIRouter
from app import auth,warehouse,admin,transactions
from fastapi.middleware.cors import  CORSMiddleware
from starlette.requests import Request




app = FastAPI()

origins = ["http://0.0.0.0:9100/"]


app.add_middleware(
    CORSMiddleware ,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"] ,
    allow_headers = ["*"]
)





app.include_router(transactions.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(warehouse.router)
@app.get("/test")
async def test():
    return {"testing":"done"}


