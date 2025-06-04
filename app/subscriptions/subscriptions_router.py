from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth.dependencies import get_current_user, get_db
from datetime import date

router = APIRouter()

@router.post("/", response_model=schemas.Subscription)
def create_subscription(sub: schemas.SubscriptionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_sub = models.Subscription(
        name=sub.name,
        price=sub.price,
        renew_period=sub.renew_period,
        end_date=sub.end_date,
        owner_id=current_user.id
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


@router.get("/", response_model=list[schemas.Subscription])
def get_subscriptions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Subscription).filter(models.Subscription.owner_id == current_user.id).all()


@router.get("/{sub_id}", response_model=schemas.Subscription)
def get_subscription(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.id == sub_id, models.Subscription.owner_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@router.put("/{sub_id}", response_model=schemas.Subscription)
def update_subscription(sub_id: int, sub_update: schemas.SubscriptionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.id == sub_id, models.Subscription.owner_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.name = sub_update.name
    sub.price = sub_update.price
    sub.renew_period = sub_update.renew_period
    sub.end_date = sub_update.end_date
    db.commit()
    db.refresh(sub)
    return sub


@router.delete("/{sub_id}")
def delete_subscription(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.id == sub_id, models.Subscription.owner_id == current_user.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(sub)
    db.commit()
    return {"detail": "Subscription deleted"}


@router.get("/summary/monthly")
def monthly_spending(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    subs = db.query(models.Subscription).filter(models.Subscription.owner_id == current_user.id).all()
    total = 0.0
    for sub in subs:
        if sub.renew_period.lower() == "monthly":
            total += sub.price
        elif sub.renew_period.lower() == "yearly":
            total += sub.price / 12
    return {"monthly_spending": round(total, 2)}


@router.post("/populate")
def populate_subscriptions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    fake_subs = [
        {"name": "Netflix", "price": 12.99, "renew_period": "monthly", "end_date": date(2025, 12, 31)},
        {"name": "Spotify", "price": 9.99, "renew_period": "monthly", "end_date": date(2025, 11, 30)},
        {"name": "Amazon Prime", "price": 119.00, "renew_period": "yearly", "end_date": date(2026, 1, 15)},
        {"name": "Adobe Creative Cloud", "price": 52.99, "renew_period": "monthly", "end_date": date(2025, 10, 20)},
    ]
    for fs in fake_subs:
        exists = db.query(models.Subscription).filter(
            models.Subscription.owner_id == current_user.id,
            models.Subscription.name == fs["name"]
        ).first()
        if not exists:
            new_sub = models.Subscription(owner_id=current_user.id, **fs)
            db.add(new_sub)
    db.commit()
    return {"detail": "Fake subscriptions added"}
