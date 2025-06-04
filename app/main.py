from fastapi import FastAPI
from app.database import engine
from app import models
from app.auth import auth_router
from app.subscriptions import subscriptions_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(subscriptions_router.router, prefix="/subscriptions", tags=["subscriptions"])
