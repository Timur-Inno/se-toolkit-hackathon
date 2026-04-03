from fastapi import APIRouter, HTTPException
from datetime import date
from ..database import database
from ..models.schemas import MenuItemCreate, MenuItemOut

router = APIRouter()

@router.get("/", response_model=list[MenuItemOut])
async def get_menu(day: date = None):
    day = day or date.today()
    rows = await database.fetch_all(
        "SELECT * FROM menu_items WHERE available_date = :day ORDER BY category, name",
        {"day": day},
    )
    return rows

@router.post("/", response_model=MenuItemOut, status_code=201)
async def create_menu_item(item: MenuItemCreate):
    available_date = item.available_date or date.today()
    row = await database.fetch_one(
        """INSERT INTO menu_items (name, price, category, available_date)
           VALUES (:name, :price, :category, :date) RETURNING *""",
        {"name": item.name, "price": item.price, "category": item.category, "date": available_date},
    )
    return row

@router.delete("/{item_id}", status_code=204)
async def delete_menu_item(item_id: int):
    result = await database.execute(
        "DELETE FROM menu_items WHERE id = :id", {"id": item_id}
    )
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
