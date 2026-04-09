from fastapi import FastAPI, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import get_hashed_passwd
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Добавляем CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели для запросов
class CartItemRequest(BaseModel):
    machinery_type_id: int
    amount: int
    start_date: str
    expiration_date: str

class CheckoutRequest(BaseModel):
    user_id: int
    items: List[CartItemRequest]

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/")
async def get_machinery_types():
    """Получить все типы техники для отображения на главной"""
    machinery_types = await MachineryType.all()
    
    if not machinery_types:
        return {
            "message": "Нет возможности аренды прямо сейчас",
            "machinery_types": []
        }
    
    types_list = []
    for m_type in machinery_types:
        types_list.append({
            "id": m_type.id,
            "type_name": m_type.type_name,
            "cost_for_hour": m_type.cost_for_hour,
            "cost_for_day": m_type.cost_for_day,
            "cost_for_month": m_type.cost_for_month
        })
    
    return {
        "machinery_types": types_list
    }

@app.get("/machinery/{machinery_id}")
async def get_machinery_details(machinery_id: int):
    """Получить детальную информацию о типе техники"""
    machinery = await MachineryType.get_or_none(id=machinery_id)
    
    if not machinery:
        raise HTTPException(status_code=404, detail="Техника не найдена")
    
    return {
        "id": machinery.id,
        "type_name": machinery.type_name,
        "cost_for_hour": machinery.cost_for_hour,
        "cost_for_day": machinery.cost_for_day,
        "cost_for_month": machinery.cost_for_month
    }

@app.post("/registration")
async def user_register(user: user_pydanticIn):
    """Регистрация пользователя"""
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_passwd(user_info["password"])
    
    # Проверяем, нет ли уже такого пользователя
    existing_user = await User.get_or_none(email=user_info["email"])
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    
    return {
        "status": "ok",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "message": f"Привет, {new_user.username}! Регистрация успешна."
    }

@app.post("/login")
async def login(login_data: LoginRequest):
    """Авторизация пользователя"""
    user = await User.get_or_none(email=login_data.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    # Проверяем пароль (временно без хеширования)
    if user.password != login_data.password:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    return {
        "status": "ok",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "message": f"Добро пожаловать, {user.username}!"
    }

@app.post("/calculate-cost")
async def calculate_cost(machinery_type_id: int, amount: int, start_date: str, expiration_date: str):
    """Рассчитать стоимость аренды (вспомогательный эндпоинт для фронтенда)"""
    machinery = await MachineryType.get_or_none(id=machinery_type_id)
    
    if not machinery:
        raise HTTPException(status_code=404, detail="Техника не найдена")
    
    # Вычисляем длительность аренды
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(expiration_date, "%Y-%m-%d")
    
    if end <= start:
        raise HTTPException(status_code=400, detail="Дата окончания должна быть позже даты начала")
    
    duration = end - start
    total_hours = duration.total_seconds() / 3600
    total_days = total_hours // 24
    remaining_hours = total_hours % 24
    
    # Рассчитываем стоимость
    total_cost = 0
    cost_breakdown = []
    
    # Стоимость за полные дни
    if total_days > 0:
        days_cost = total_days * machinery.cost_for_day * amount
        total_cost += days_cost
        cost_breakdown.append({
            "type": "days",
            "count": int(total_days),
            "rate": machinery.cost_for_day,
            "amount": amount,
            "subtotal": days_cost
        })
    
    # Стоимость за оставшиеся часы
    if remaining_hours > 0:
        hours_cost = remaining_hours * machinery.cost_for_hour * amount
        total_cost += hours_cost
        cost_breakdown.append({
            "type": "hours",
            "count": remaining_hours,
            "rate": machinery.cost_for_hour,
            "amount": amount,
            "subtotal": hours_cost
        })
    
    return {
        "machinery_type_id": machinery_type_id,
        "type_name": machinery.type_name,
        "amount": amount,
        "start_date": start_date,
        "expiration_date": expiration_date,
        "total_days": int(total_days),
        "total_hours": total_hours,
        "remaining_hours": remaining_hours,
        "total_cost": total_cost,
        "cost_breakdown": cost_breakdown
    }

@app.post("/offer/create")
async def create_offer(checkout_data: CheckoutRequest):
    """Создание заказов после подтверждения"""
    # Проверяем существование пользователя
    user = await User.get_or_none(id=checkout_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    created_offers = []
    
    for item in checkout_data.items:
        # Проверяем существование техники
        machinery = await MachineryType.get_or_none(id=item.machinery_type_id)
        if not machinery:
            raise HTTPException(status_code=404, detail=f"Техника с ID {item.machinery_type_id} не найдена")
        
        # Вычисляем стоимость (можно переиспользовать логику из /calculate-cost)
        start = datetime.strptime(item.start_date, "%Y-%m-%d")
        end = datetime.strptime(item.expiration_date, "%Y-%m-%d")
        duration = end - start
        
        total_hours = duration.total_seconds() / 3600
        total_days = total_hours // 24
        remaining_hours = total_hours % 24
        
        total_cost = 0
        if total_days > 0:
            total_cost += total_days * machinery.cost_for_day * item.amount
        if remaining_hours > 0:
            total_cost += remaining_hours * machinery.cost_for_hour * item.amount
        
        # Создаём запись в UserOffer
        offer = await UserOffer.create(
            userId_id=checkout_data.user_id,
            machineryTypeId_id=item.machinery_type_id,
            amount=item.amount,
            total_cost=total_cost,
            hours_offered=int(remaining_hours) if remaining_hours > 0 else 0,
            days_offered=int(total_days),
            start_date=start.date(),
            expiration_date=end.date(),
            status="active",
            offer_image=""  # Пока пусто
        )
        
        created_offers.append({
            "id": offer.id,
            "machinery_type": machinery.type_name,
            "amount": item.amount,
            "total_cost": total_cost,
            "start_date": item.start_date,
            "expiration_date": item.expiration_date,
            "status": "active"
        })
    
    return {
        "status": "ok",
        "message": f"Создано {len(created_offers)} заказов",
        "offers": created_offers
    }

@app.get("/offers/user/{user_id}")
async def get_user_offers(user_id: int):
    """Получить все заказы пользователя"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    offers = await UserOffer.filter(userId_id=user_id).prefetch_related("machineryTypeId")
    
    result = []
    for offer in offers:
        result.append({
            "id": offer.id,
            "machinery_type": offer.machineryTypeId.type_name,
            "amount": offer.amount,
            "total_cost": offer.total_cost,
            "start_date": offer.start_date.isoformat(),
            "expiration_date": offer.expiration_date.isoformat(),
            "status": offer.status,
            "days_offered": offer.days_offered,
            "hours_offered": offer.hours_offered
        })
    
    return {"offers": result}

@app.get("/offer/{offer_id}")
async def get_offer_details(offer_id: int):
    """Получить детали конкретного заказа"""
    offer = await UserOffer.get_or_none(id=offer_id).prefetch_related("machineryTypeId", "userId")
    
    if not offer:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return {
        "id": offer.id,
        "user": {
            "id": offer.userId.id,
            "username": offer.userId.username,
            "email": offer.userId.email
        },
        "machinery_type": {
            "id": offer.machineryTypeId.id,
            "type_name": offer.machineryTypeId.type_name
        },
        "amount": offer.amount,
        "total_cost": offer.total_cost,
        "start_date": offer.start_date.isoformat(),
        "expiration_date": offer.expiration_date.isoformat(),
        "status": offer.status,
        "days_offered": offer.days_offered,
        "hours_offered": offer.hours_offered
    }

register_tortoise(
    app, 
    db_url="sqlite://database.sqlite3", 
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
