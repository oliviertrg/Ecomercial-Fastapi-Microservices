from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import es
from fastapi.encoders import jsonable_encoder
from app import auth2,auth2_users
import requests
import json
from datetime import datetime

router = APIRouter (
    prefix = "/orders",
    tags = ["orders"]
)




