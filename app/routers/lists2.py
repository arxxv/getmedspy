from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from starlette.responses import JSONResponse
from .. import database, schemas, oauth2, db
import random

router = APIRouter(
    prefix='/orders',
    tags=['Orders']
)

database = db.create_db()
c_o, c_u = database['ordersc'], database['usersc']

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.ResponseOrderModel])
def get_all_orders():
    orders = list(c_o.find({"status":"active"}))
    return orders

@router.get('/{id}',  status_code=status.HTTP_200_OK, response_model=schemas.ResponseOrderModel)
def get_order_with_id(id: int):
    query = { "id": str(id) }
    orders = list(c_o.find(query))
    if len(orders) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
    return orders[0]

@router.post('/', response_model=schemas.ResponseCreateOrderModel, status_code=status.HTTP_201_CREATED)
def create_order(orderobj: schemas.OrderModel, user: str = Depends(oauth2.get_current_user)):
    orderobj = orderobj.dict()
    uid = user.id
    orderobj['status'] = "active"
    orderobj['d_uid'] = ''
    orderobj['uid'] = uid
    orderobj['reputation'] = 10+2*len(orderobj['items'])
    if len(orderobj['name']) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name the Order")
    if len(orderobj['items'])+len(orderobj['symptoms']) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Items and Symptoms Cannot Be Empty")

    uquery = { "id": uid }
    users = list(c_u.find(uquery))
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found")
    user = users[0]

    if len(user['address']) == 0 or len(user['payments']) == 0 or len(user['phone']) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Complete User Details First")

    orderobj['uaddress'] = user['address'][0]
    orderobj['uphone'] = user['phone']
    orderobj['upayments'] = user['payments']

    flag = True
    while flag:
        orderid = str(random.randrange(1, 1000000))
        oquery = { "id": orderid }
        orders = list(c_o.find(oquery))
        if len(orders) == 0:
            flag = False
            orderobj['id'] = orderid

    uupdatedValues = {"$push":{"orders":orderid, "created_orders":orderid}}
    
    c_u.update_one(uquery, uupdatedValues)
    c_o.insert_one(orderobj)
    return orderobj 


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: int, user: str = Depends(oauth2.get_current_user)):
    uid = user.id
    id = str(id)

    uquery = { "id": uid }

    oquery = { "id": id }
    orders = list(c_o.find(oquery))
    if len(orders) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
    order = orders[0]

    if order['status'] == "completed":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order Is Already Processed")
    if order['status'] != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Order Is Not In Active State")

    updatedValues = {"$pull":{"orders":id, "created_orders":id}}
    c_u.update_one(uquery, updatedValues)
    c_o.delete_one(oquery)
    return JSONResponse(content="Success")

@router.put('/{id}/accept', status_code=status.HTTP_200_OK)
def accept_order(id: int, user: str = Depends(oauth2.get_current_user)):
    uid = user.id
    id = str(id)

    oquery = { "id": id }
    u1query = { "id" : uid }

    order = list(c_o.find(oquery))
    if len(order) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
    order = order[0]

    if order['uid'] == uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You Can't Accept Your List")
    if order['status'] != 'active':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Order Already Processed")

    u2query = { "id" : order['uid'] }
    oupdatedValues = {"$set":{"status":"accepted", "d_uid":uid}}
    u1updatedValues = {"$push":{"orders":id, "accepted_orders":id}}
    u2updatedValues = {"$inc":{"reputation":-order['reputation']}}

    c_o.update_one(oquery, oupdatedValues)
    c_u.update_one(u1query, u1updatedValues)
    c_u.update_one(u2query, u2updatedValues)
    return JSONResponse(content="Success")

@router.put('/{id}/reject', status_code=status.HTTP_200_OK)
def reject_order(id: int, user: str = Depends(oauth2.get_current_user)):
    uid = user.id
    id = str(id)

    oquery = { "id": id }
    u1query = { "id" : uid }

    order = list(c_o.find(oquery))
    if len(order) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
    order = order[0]

    if order['status'] != 'accepted':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You Cannot Reject The Order")

    u2query = { "id" : order['uid'] }
    oupdatedValues = {"$set":{"status":"active", "d_uid":""}}
    u1updatedValues = {"$pull":{"orders":id, "accepted_orders":id}, "$inc":{"reputation":order['reputation']}}
    u2updatedValues = {"$inc":{"reputation":order['reputation']}}

    c_o.update_one(oquery, oupdatedValues)
    c_u.update_one(u1query, u1updatedValues)
    c_u.update_one(u2query, u2updatedValues)
    return JSONResponse(content="Success")
    
@router.put('/{id}/taken', status_code=status.HTTP_200_OK)
def take_order(id: int, user: str = Depends(oauth2.get_current_user)):
    id = str(id)

    oquery = { "id": id }
    order = list(c_o.find(oquery))
    if len(order) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
    order = order[0]

    if order['status'] != 'accepted':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order Has To Be Accepted First")
    if order['status'] == 'taken':
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Order Already Taken")

    oupdatedValues = {"$set":{"status":"taken"}}
    c_o.update_one(oquery, oupdatedValues)
    return JSONResponse(content="Success")
    
@router.put('/{id}/complete', status_code=status.HTTP_200_OK)
def complete_order(id: int, user: str = Depends(oauth2.get_current_user)):    
    id = str(id)
    oquery = { "id": id }
    uquery = { "id": user.id }

    order = list(c_o.find(oquery))
    if len(order) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
    order = order[0]

    if order['status'] != 'taken':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order Has To Be Taken First")
    if order['status'] == 'completed':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order Already Processed")

    oupdatedValues = {"$set":{"status":"completed"}}
    uupdatedValues = {"$inc":{"reputation":order['reputation']}}

    c_o.update_one(oquery, oupdatedValues)
    c_u.update_one(uquery, uupdatedValues)
    return JSONResponse(content="Success")