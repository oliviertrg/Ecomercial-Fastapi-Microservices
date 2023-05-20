from jose import JWSError,jwt
from app import schema
from fastapi import Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta
from decouple import config


SECRET_KEY = config("SECRET_KEY_USERS")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))

oath2_schema = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict) :
    to_token = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_token.update({"exp" : expire})
    encode_jwt = jwt.encode(to_token,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

def get_current_user(token : str = Depends(oath2_schema)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"COULD NOT VALIDATE CREDENTIALS",
                                          headers={"WWW-Authenticate": "Bearer"})

    token_ = verify_access_token(token, credentials_exception)
    return token_

def verify_access_token(token : str,credentials_exception) :
    try :
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        user_id : str = payload.get("user_id")
        if user_id is None :
            raise credentials_exception
        token_data = schema.tokendata(id = user_id)
    # except JWSError:
    # we were try but this shit ain't work
    except :
        raise credentials_exception
    return token_data
