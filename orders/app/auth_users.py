from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schema,utils,auth2
from app.config import curso

router = APIRouter(tags=["Authentication"])

@router.post('/login',response_model = schema.token)
async def login(user_credentials : OAuth2PasswordRequestForm = Depends()):
    db = curso()
    c = db.cursor()
    b = (user_credentials.username)
    sql = (f'''SELECT * FROM "users" where "email" = '{b}' ;''')
    c.execute(sql)
    user = c.fetchall()
    if len(user) == 0 :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = f"Invalid Credentails"
        )
    if not utils.verify(user_credentials.password,user[0][3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Credentails"
        )
    access_token = auth2.create_access_token(data={"user_id": user[0][0]})
    return {"access_token": access_token, "token_type": "bearer"}

