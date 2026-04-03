from pydantic import BaseModel
from datetime import date
from typing import Optional

class MenuItemCreate(BaseModel):
    name: str
    price: float
    category: str = "main"
    available_date: Optional[date] = None

class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    category: str
    available_date: date

class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    telegram_user_id: int
    telegram_username: Optional[str] = None
    items: list[OrderItemIn]

class OrderOut(BaseModel):
    id: int
    telegram_user_id: int
    telegram_username: Optional[str]
    status: str
    items: list[OrderItemIn]
