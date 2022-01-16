from pydantic import BaseModel, EmailStr
from typing import List, Optional

class OrderModel(BaseModel):
    items: List
    name: str
    reputation: int
    symptoms: List    

class ResponseCreateOrderModel(BaseModel):
    id: int

class ResponseOrderModel(BaseModel):
    id: int
    name: str
    uid: EmailStr
    items: List
    status: str
    d_uid: str
    reputation: int
    symptoms: List
    upayments: str
    uphone: str
    uaddress: str

class GetUserModel(BaseModel):
    id: str

class UpdateOrderModel(BaseModel):
    items: List

class RegisterUserModel(BaseModel):
    name: str
    id: EmailStr
    password: str

class ResponseRegisterUserModel(BaseModel):
    id: EmailStr

class ResponseUpdateOrderModel(BaseModel):
    items: List

class ResponseUserModel(BaseModel):
    id: EmailStr
    name: str
    orders: List
    created_orders: List
    accepted_orders: List
    phone: str
    address: List
    payments: str
    time_saved: int
    reputation: int

class UserProfileOrdersModel(BaseModel):
    orders: List[ResponseOrderModel]

class ResponseUserModelInfo(BaseModel):
    id: EmailStr
    name: str
    orders: List[ResponseOrderModel]
    created_orders: List[ResponseOrderModel]
    accepted_orders: List[ResponseOrderModel]
    phone: str
    address: List
    payments: str
    time_saved: int
    reputation: int

class ResponseUserProfileModel(BaseModel):
    id: EmailStr
    name: str
    phone: str
    address: List
    payments: str
    time_saved: int
    reputation: int
    created_orders: int
    accepted_orders: int
    completed_orders: int

class ResponseLoginModel(BaseModel):
    id: EmailStr
    name: str
    phone: str
    address: List
    payments: str
    time_saved: int
    reputation: int
    access_token: str
    token_type: str


class UserLoginModel(BaseModel):
    id: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class UpdateUserModel(BaseModel):
    payments: Optional[str] = ''
    phone: Optional[str] = ''
    address: Optional[str] = ''