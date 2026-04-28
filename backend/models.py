import pydantic
from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk = True, index = True)
    username = fields.CharField(max_length=20, null = False, unique = True)
    email = fields.CharField(max_length=200, null = False, unique = True)
    password = fields.CharField(max_length = 100, null = False)
    is_verified = fields.BooleanField(default = False)


class MachineryType(Model):
    id = fields.IntField(pk=True, index=True)
    type_name = fields.CharField(max_length=20, null=False, unique=True)
    cost_for_hour = fields.FloatField(null=False)
    cost_for_day = fields.FloatField(null=False)
    cost_for_month = fields.FloatField(null=False)


class UserOffer(Model):
    id = fields.IntField(pk = True, index = True)
    userId = fields.ForeignKeyField('models.User', related_name='offerUserID', null=False)
    machineryTypeId = fields.ForeignKeyField('models.MachineryType', related_name='offers', null=False)
    amount = fields.IntField(null=False, default=1)
    total_cost = fields.FloatField(null=False)
    hours_offered = fields.IntField(null=True, default=0)
    days_offered = fields.IntField(null=True, default=0)
    start_date = fields.DateField(null=False, default=datetime.utcnow)
    expiration_date = fields.DateField(null=False)
    status = fields.CharField(max_length=20, null=False, default='active')
    offer_image = fields.CharField(max_length=255, null=True)


# useless for now
class AllOffers(Model):
    id = fields.IntField(pk = True, index = True)
    offerId = fields.ForeignKeyField('models.UserOffer')
    offer_cost = fields.FloatField(null=False)
    offer_expiration_date = fields.ForeignKeyField('models.UserOffer', related_name = 'exprn_date')


# adds a machinery type
class MachineryCreate(BaseModel):
    type_name: str
    cost_for_hour: float
    cost_for_day: float
    cost_for_month: float

   
user_pydantic = pydantic_model_creator(User, name = "User", exclude=("is_verified"))
user_pydanticIn = pydantic_model_creator(User, name = "UserIn", exclude_readonly=True, exclude=("is_verified", "join_date"))
user_pydanticOut = pydantic_model_creator(User, name = "UserOut", exclude=("password", ))

machineryType_pydantic = pydantic_model_creator(MachineryType, name = "MachineryType")

user_offer_pydantic = pydantic_model_creator(UserOffer, name="UserOffer")
user_offer_pydanticIn = pydantic_model_creator(UserOffer, name="UserOfferIn", exclude_readonly=True)

