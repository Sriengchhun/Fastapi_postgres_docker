# pip install database
from curses import meta
from datetime import datetime
from doctest import Example
from http.client import ResponseNotReady
from imp import acquire_lock
from re import A, S
from urllib import response
# from argon2 import PasswordHasher
from fastapi import FastAPI
import databases, sqlalchemy, uuid, datetime
import asyncpg   ## need to import this modual for DATABASE_URL
from pydantic import BaseModel, Field
from typing import List


## Postgres Database
### DATABASE_URL=postgres://{user}:{password}@{hostname}:{port}/{database-name}
# DATABASE_URL = "postgresql://postgres:chhun@127.0.0.1:5432/postgres"
DATABASE_URL= "postgresql://chhun:1234@db:5432/mydb"


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
    ## Create table in database
users = sqlalchemy.Table(
    "My_table",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("gender", sqlalchemy.CHAR),
    sqlalchemy.Column("create_at", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.CHAR),
    # sqlalchemy.Column("age", sqlalchemy.Integer),
)
    ## Connect and create table
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

## Models
class UserList(BaseModel):
    id          : str
    username    : str
    password    : str
    first_name  : str
    last_name   : str
    gender      : str
    create_at   : str
    status      : str

class UserEntry(BaseModel):
    username    : str = Field(..., example="Chhun")
    password    : str = Field(..., example="1234")
    first_name  : str = Field(..., example="Srieng")
    last_name   : str = Field(..., example="Chheang")
    gender      : str = Field(..., example="M")

class User_update(BaseModel):
    id          : str = Field(..., example="Enter your id")
    first_name  : str = Field(..., example="Srieng")
    last_name   : str = Field(..., example="Chheang")
    gender      : str = Field(..., example="M")
    status      : str = Field(..., example="1")

class UserDelete(BaseModel):
    id: str = Field(..., example="Enter your ID")





app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/users", response_model=List[UserList])
async def find_all_users():
    query = users.select()
    return await database.fetch_all(query)

@app.post ("/users", response_model=UserList)
async def register_user(user: UserEntry):
    gID     = str(uuid.uuid1())
    gDate   = str(datetime.datetime.now())
    query   = users.insert().values(
        id          = gID,
        username    = user.username,
        password    = user.password,
        first_name  = user.first_name,
        last_name   = user.last_name,
        gender      = user.gender,
        create_at   = gDate,
        status      = "1"
    )

    await database.execute(query)
    return {
        "id": gID,
        **user.dict(),
        "create_at":gDate,
        "status":"1"
    }

@app.get("/users/{userId}", response_model=UserList)
async def find_user_by_id(userId: str):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)


@app.put("/users", response_model=UserList)
async def update_user(user: User_update):
    gDate = str(datetime.datetime.now())
    query = users.update().\
        where(users.c.id == user.id). \
        values(
            first_name  = user.first_name,
            last_name   = user.last_name,
            gender      = user.gender,
            status      = user.status,
            create_at   = gDate,
        )
    await database.execute(query)

    return await find_user_by_id(user.id)

@app.delete("/users/{userId}")
async def delete_user(user:UserDelete):
    query = users.delete().where(users.c.id == user.id)
    await database.execute(query)

    return {
        "status"    : True,
        "message"   : "This user has been deleted successfully"
    }



## Check module in pip : pip list