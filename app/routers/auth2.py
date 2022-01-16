from os import access
from fastapi import APIRouter, status, HTTPException, Response, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemas, database, utils, oauth2, db


router = APIRouter(tags=['Authentication'])

# c_o, c_u = database.create_db()/
database = db.create_db()
c_o, c_u = database['ordersc'], database['usersc']



@router.post('/login', response_model=schemas.ResponseLoginModel)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    user_credentials = user_credentials
    email = user_credentials.username
    password = user_credentials.password
    
    query = { "id": email }
    users = list(c_u.find(query))

    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials") 
    user = users[0]

    if not utils.verify(password, user['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials") 
    
    access_token = oauth2.create_access_token(data = {"user_id": email})

    user["access_token"] = access_token
    user["token_type"] = "bearer"

    return user