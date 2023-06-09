from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schema,utils,auth2_admin
from app.config import curso

router = APIRouter(tags=["Authentication"])

@router.post('/login',response_model = schema.token)
async def login(user_credentials : OAuth2PasswordRequestForm = Depends()):
    db = curso()
    c = db.cursor()
    b = (user_credentials.username)
    sql = (f'''SELECT * FROM "admins" where "email" = '{b}' ;''')
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
    if user[0][4] == False :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    access_token = auth2_admin.create_access_token(data={"admins_id": user[0][0]})
    return {"access_token": access_token, "token_type": "bearer"}



