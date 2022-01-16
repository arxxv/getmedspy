from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from .. import database, schemas, utils, oauth2, db
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix='/users',
    tags=['Users']
)

database = db.create_db()
c_o, c_u = database['ordersc'], database['usersc']

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.ResponseUserModel])
def get_all_users():
    users = list(c_u.find())
    return users

@router.post('/',  status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseUserModel)
def create_user(user: schemas.RegisterUserModel):
    user = user.dict()
    user['created_orders'] = []
    user['accepted_orders'] = []
    user['orders'] = []
    user['reputation'] = 100
    user['time_saved'] = 0
    user['phone'] = ''
    user['address'] = []
    user['payments'] = ''
    user['password'] = utils.hash(user['password'])
    id = user['id']
    
    query = { "id": id }
    users = list(c_u.find(query))
    if len(users) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The Email Is Already Registered")
    
    c_u.insert_one(user)
    return JSONResponse(content="Success")
        
@router.get('/info/all', status_code=status.HTTP_200_OK, response_model=schemas.ResponseUserModelInfo)
def get_user_with_email(user: str = Depends(oauth2.get_current_user)):
    id = user.id
    query = { "id": id }
    users = list(c_u.find(query))
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found")
    user = users[0]

    user['created_orders'] = list(c_o.find({"id":{"$in":user['created_orders']}}))
    user['accepted_orders'] = list(c_o.find({"id":{"$in":user['accepted_orders']}}))
    user['orders'] = list(c_o.find({"id":{"$in":user['orders']}}))
    return user

@router.get('/info/useful', status_code=status.HTTP_200_OK, response_model=schemas.ResponseUserProfileModel)
def get_user_with_email(user: str = Depends(oauth2.get_current_user)):
    id = user.id
    
    query = { "id": id }
    users = list(c_u.find(query))
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found")
    user = users[0]

    userobject = {}
    userobject['reputation'] = user['reputation']
    userobject['id'] = user['id']
    userobject['name'] = user['name']
    userobject['phone'] = user['phone']
    userobject['time_saved'] = user['time_saved']
    userobject['payments'] = user['payments']
    userobject['address'] = user['address']
    userobject['created_orders'] = len(user['created_orders'])
    userobject['accepted_orders'] = 0
    userobject['completed_orders'] = 0

    for orderid in user['accepted_orders']:
        query = { "id": orderid }
        orders = list(c_o.find(query))
        if len(orders) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order Not Found")
        order = orders[0]

        if order['status'] == 'active' or order['status'] == 'taken':
            userobject['accepted_orders'] += 1
        else:
            userobject['completed_orders'] += 1

    return userobject
        
@router.get('/orders/all', status_code=status.HTTP_200_OK, response_model=schemas.UserProfileOrdersModel)
def get_user_orders(user: str = Depends(oauth2.get_current_user)):
    id = user.id

    query = { "id": id }
    users = list(c_u.find(query))
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found")
    user = users[0]

    orders = {"orders":list(c_o.find({"id":{"$in":user['orders']}}))}
    return orders

@router.get('/orders/created', status_code=status.HTTP_200_OK, response_model=schemas.UserProfileOrdersModel)
def get_user_orders(user: str = Depends(oauth2.get_current_user)):
    id = user.id

    query = { "id": id }
    users = list(c_u.find(query))
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found")
    user = users[0]

    created_orders = {"orders":list(c_o.find({"id":{"$in":user['created_orders']}}))}
    return created_orders

@router.get('/orders/accepted', status_code=status.HTTP_200_OK, response_model=schemas.UserProfileOrdersModel)
def get_user_orders(user: str = Depends(oauth2.get_current_user)):
    id = user.id

    query = { "id": id }
    users = list(c_u.find(query))
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found")
    user = users[0]

    accepted_orders = {"orders":list(c_o.find({"id":{"$in":user['accepted_orders']}}))}
    return accepted_orders

@router.put('/', status_code=status.HTTP_200_OK)
def update_user(data: schemas.UpdateUserModel, user: str = Depends(oauth2.get_current_user)):
    id = user.id
    data = data.dict()
    
    query = { "id": id }

    updatedValues = {"$set":{}, "$push":{}}
    if len(data['payments']) > 0: 
        updatedValues["$set"]["payments"] = data['payments']
    if len(data['phone']) > 0: 
        updatedValues["$set"]["phone"] = data['phone']
    if len(data['address']) > 0:
        updatedValues["$push"]["address"] = data['address']
    
    
    c_u.update_one(query, updatedValues)
    return JSONResponse(content="Success")
