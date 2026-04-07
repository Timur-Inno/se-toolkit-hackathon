from fastapi import APIRouter, HTTPException
from datetime import date
from pydantic import BaseModel
from ..database import database
from ..models.schemas import MenuItemCreate, MenuItemOut

router = APIRouter()

@router.get("/", response_model=list[MenuItemOut])
async def get_menu(day: date = None, venue: str = None):
    day = day or date.today()
    dow = day.weekday()
    if venue:
        weekly = await database.fetch_all(
            """SELECT -w.id as id, w.name, w.price, w.category, w.venue, :day as available_date
               FROM weekly_menu w
               WHERE w.venue = :venue AND w.day_of_week = :dow""",
            {"venue": venue, "dow": dow, "day": day},
        )
        manual = await database.fetch_all(
            """SELECT * FROM menu_items
               WHERE available_date = :day AND venue = :venue
               ORDER BY category, name""",
            {"day": day, "venue": venue},
        )
    else:
        weekly = await database.fetch_all(
            """SELECT -w.id as id, w.name, w.price, w.category, w.venue, :day as available_date
               FROM weekly_menu w WHERE w.day_of_week = :dow""",
            {"dow": dow, "day": day},
        )
        manual = await database.fetch_all(
            """SELECT * FROM menu_items WHERE available_date = :day
               ORDER BY venue, category, name""",
            {"day": day},
        )
    seen = set()
    result = []
    for item in list(weekly) + list(manual):
        key = (item["venue"], item["name"].lower())
        if key not in seen:
            seen.add(key)
            result.append(dict(item))
    return result

@router.post("/", response_model=MenuItemOut, status_code=201)
async def create_menu_item(item: MenuItemCreate):
    available_date = item.available_date or date.today()
    row = await database.fetch_one(
        """INSERT INTO menu_items (name, price, category, venue, available_date)
           VALUES (:name, :price, :category, :venue, :date) RETURNING *""",
        {"name": item.name, "price": item.price, "category": item.category,
         "venue": item.venue, "date": available_date},
    )
    return row

@router.delete("/{item_id}", status_code=204)
async def delete_menu_item(item_id: int):
    result = await database.execute(
        "DELETE FROM menu_items WHERE id = :id", {"id": item_id}
    )
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")

# Weekly menu endpoints
class WeeklyItemCreate(BaseModel):
    venue: str
    day_of_week: int
    name: str
    price: float
    category: str = "main"

class WeeklyItemOut(BaseModel):
    id: int
    venue: str
    day_of_week: int
    name: str
    price: float
    category: str

@router.get("/weekly", response_model=list[WeeklyItemOut])
async def get_weekly(venue: str = None):
    if venue:
        rows = await database.fetch_all(
            "SELECT * FROM weekly_menu WHERE venue = :venue ORDER BY day_of_week, category, name",
            {"venue": venue},
        )
    else:
        rows = await database.fetch_all(
            "SELECT * FROM weekly_menu ORDER BY venue, day_of_week, category, name"
        )
    return rows

@router.post("/weekly", response_model=WeeklyItemOut, status_code=201)
async def create_weekly_item(item: WeeklyItemCreate):
    row = await database.fetch_one(
        """INSERT INTO weekly_menu (venue, day_of_week, name, price, category)
           VALUES (:venue, :dow, :name, :price, :category) RETURNING *""",
        {"venue": item.venue, "dow": item.day_of_week, "name": item.name,
         "price": item.price, "category": item.category},
    )
    return row

@router.delete("/weekly/{item_id}", status_code=204)
async def delete_weekly_item(item_id: int):
    await database.execute("DELETE FROM weekly_menu WHERE id = :id", {"id": item_id})
