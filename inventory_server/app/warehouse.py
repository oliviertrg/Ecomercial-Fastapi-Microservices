from fastapi import FastAPI ,Response,status ,HTTPException,APIRouter,Depends, Request
from app.config import es,curso

from app import auth2_admin

from datetime import datetime

router = APIRouter (
    prefix = "/merchandise",
    tags = ["merchandise"]
)

es = es()
@router.get('/views/query=*')
async def view_all():
  try:
    r = list()
    ree = es.search(index="grocery_store", query={"match_all": {}})
    if len(ree['hits']['hits']) == 0 :
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
    for i in ree['hits']['hits']:
       c = i['_source']
       c.update({"id":i['_id']})
       r.append(c) 
     
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return r

@router.get('/views/query={search_query}')
async def view(search_query : str):
  try:
    r = list()
    ree = es.search(index="grocery_store",query={"multi_match": {"query": search_query,
                                                                 "fields":["product","type","_id"]}})
    if len(ree['hits']['hits']) == 0 :
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
    for i in ree['hits']['hits']:
       c = i['_source']
       c.update({"id":i['_id']})
       r.append(c) 
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  return r


@router.post('/import',status_code=status.HTTP_201_CREATED)
async def import_merchandise(request: Request,current_admin : int = Depends(auth2_admin.get_current_user)):
 
 body = await request.json()
 if "quantity" not in body :
     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"IMPORT PRODUCTS SHOULD INCLUDE QUANTITY")
 if "product" not in body :
     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"IMPORT PRODUCTS SHOULD INCLUDE PRODUCT")
 try: 
      db = curso()
      c = db.cursor() 
      user = {"users_id_who_created" : int(current_admin.id),
              'timestamp': datetime.now()}
      body.update(user)
      resp = es.index(index="grocery_store", document=body)
      sql = """insert into inventory(item_id,item_name,quantity) values(%s,%s,%s) ; """
      x = (resp['_id'],body["product"],int(body["quantity"]))
      c.execute(sql,x)
      db.commit()
 except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{e}")
     
 return {
         "id_product":resp['_id'],
         "status":resp['result']
         }



@router.put('/update_products/{product_id}',status_code=status.HTTP_200_OK)
async def update_product(product_id : str,request: Request ,current_admin : int = Depends(auth2_admin.get_current_user)):
    try:
     body = await request.json()
     if "quantity" in body :
       db = curso()
       c = db.cursor()
       sql = f""" update inventory set quantity = (quantity + {int(body["quantity"])})
              where item_id = '{product_id}'; """
       c.execute(sql)
       db.commit()
     user = {"users_id_who_created" : int(current_admin.id)}
     body.update(user)
     resp = es.update(index="grocery_store",id=product_id,doc=body)
    except Exception as ex:
     print(f"Error {ex}")
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=f"{ex}")

    return {
            "id_product":resp['_id'],
            "status":resp['result']
            }

@router.delete('/delete/{product_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(product_id : str,current_admin : int = Depends(auth2_admin.get_current_user)):
  try:
    db = curso()
    c = db.cursor()
    resp = es.delete(index="grocery_store", id=product_id) 
    sql =f"""delete from "inventory" where item_id = '{product_id}'"""
    c.execute(sql)
    db.commit()
  except Exception as e:
     print(f"Error {e}")
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="CAN'T FIND ANY PRODUCTS ")
  
  return Response(status_code=status.HTTP_204_NO_CONTENT)









    





