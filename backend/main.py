from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import *
from authentication import (get_hashed_passwd)
#signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient


app = FastAPI()


@app.post("/registration")
async def user_register(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_passwd(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
            "status" : "ok",
            "data" : f"Hello {new_user.username}, thanks for join. Check your email"
            }


@app.post("/create_offer")
async def create_offer(offer: user_offer_pydanticIn):
    offer_obj = await UserOffer.create(**offer.dict())
    return await user_offer_pydantic.from_tortoise_orm(offer_obj)


@app.get("/offers")
async def get_offers():
    return await user_offer_pydantic.from_queryset(UserOffer.all())


@app.get("/")
def index():
    return {"Message": "Hello world"}


register_tortoise(
        app, 
        db_url="sqlite://database.sqlite3", 
        modules={"models": ["models"]},
        generate_schemas=True,
        add_exception_handlers=True
        )
