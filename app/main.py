from typing import Union

from pydantic import BaseModel

from app.projects import crud
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="P-Cube API",
    description="P-Cube API built for Neo4j with FastAPI",
    version=0.1,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(
    crud.router,
    prefix="/api/projects",
    tags=["Project Node"],
)

####### old code #######
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def fake_hash_password(password: str):
    return "faked" + password


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[str, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded",
        email="a@b.com",
        full_name="John Doe",
        disabled=False,
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user


@app.get("/")
async def root():
    return {"Message": "Hello World"}


@app.get("users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/items")
async def read_item(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
