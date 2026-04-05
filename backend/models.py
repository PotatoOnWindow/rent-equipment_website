from tortoise import Model
from pydantic import BaseModel


class User(Model):
    id = fields.InterField(pk = True, index = True)
    username = fields.CharField(max_length=20, null = False, unique = True)
    email = fields.CharField(max_length=200, null = False, unique = True)
    password = fields.CharField(max_length = 100, null = False)
    is_verified = fields.BooleanField(default = False)

# not done
class MachineryType(Model):
    id = fields.InterField(pk = True, index = True)
    type_name = fields.CharField(max_length=20, null = False, unique = True)
    
