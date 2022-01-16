from fastapi import FastAPI
from .routers import users2, lists2, auth2
from . import database, db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# c_o, c_u = database.create_db()
database= db.create_db()


app.include_router(users2.router)
app.include_router(lists2.router)
app.include_router(auth2.router)


