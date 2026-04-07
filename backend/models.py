from tortoise import Model
from pydantic import BaseModel
from datetime import datetime


class User(Model):
    id = fields.IntField(pk = True, index = True)
    username = fields.CharField(max_length=20, null = False, unique = True)
    email = fields.CharField(max_length=200, null = False, unique = True)
    password = fields.CharField(max_length = 100, null = False)
    is_verified = fields.BooleanField(default = False)


class MachineryType(Model):
    id = fields.IntField(pk = True, index = True)
    type_name = fields.CharField(max_length=20, null = False, unique = True)
    cost_for_hour = fields.FloatField(null = False)
    cost_for_day = fields.FloatField(null = False)
    cost_for_month = fields.FloatField(null = False)


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
    offer_image = fields.CharField(max_length=20, null=False)


class AllOffers(Model):
    id = fields.IntField(pk = True, index = True)
    offerId = fields.ForeignKeyField('models.UserOffer')
    offer_cost = fields.FloatField(null=False)
    offer_expiration_date = fields.ForeignKeyField('models.UserOffer', related_name = 'exprn_date')

    
