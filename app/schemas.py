from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    email: str
    password: str

class SubscriptionBase(BaseModel):
    name: str
    price: float
    renew_period: str
    end_date: date

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
