from fastapi import FastAPI,Depends,status ,HTTPException,APIRouter,Response
from app.config import curso
from app.utils import hashpass
from app.schema import update_users,users
from app import auth2


router = APIRouter (
         prefix = "/users" ,
         tags = ["users"]
)

db = curso()
c = db.cursor()

@router.post('/register',status_code=status.HTTP_201_CREATED)
def register(new_user : users):
  new_pass = hashpass(new_user.password)
  new_user.password = new_pass
  x = (new_user.username,new_user.email,new_user.password,new_user.is_actice,new_user.is_staff)
  sql = (""" insert into users(usersname,email,passwords,is_active,is_staff) 
             values (%s,%s,%s,%s,%s) ; """)
  c.execute(sql,x)
  db.commit()
  return {"username":new_user.username,
          "email":new_user.email }
@router.put('/update/{id}',response_model = update_users)
def update_user(id : int,new_update_user : update_users,current_user : int = Depends(auth2.get_current_user)):
    sql = f'''select * from "users"	where "user_id" = {id} ;'''
    c.execute(sql)
    x = c.fetchall()

    if len(x) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} does not exist")
    if id != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    else:
        try:
            sql1 = f'''UPDATE "users" SET 
                           usersname = '{new_update_user.username}' ,
                           email = '{new_update_user.email}' ,
                           is_staff = '{new_update_user.is_staff}'
                           WHERE user_id = {id} ;'''
            c.execute(sql1)
            db.commit()
        except Exception as e:
            print(f"Error {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"{e}")
            
        return new_update_user

@router.delete('/delete/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int,current_user : int = Depends(auth2.get_current_user)):
  sql = f'''select * from "users"	where "user_id" = {id} ;'''
  c.execute(sql)
  x = c.fetchall()

  if len(x) == 0 :
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"user with id: {id} does not exist")
  if id != int(current_user.id) :
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                          detail="Not authorized to perform requested action")
  else:
      sql1 = f'''delete from "users" where "user_id" = {id} ;'''
      c.execute(sql1)
      db.commit()

  return Response(status_code=status.HTTP_204_NO_CONTENT)


