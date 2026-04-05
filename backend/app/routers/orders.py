from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from ..database import database
from ..models.schemas import OrderCreate, OrderOut, OrderItemIn

router = APIRouter()
BOT_NOTIFY_URL = os.getenv("BOT_NOTIFY_URL", "http://bot:9000/notify")

VALID_TRANSITIONS = {
    "pending": ["ready", "cancelled"],
    "ready": ["served", "cancelled"],
    "served": [],
    "cancelled": [],
}

@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(order: OrderCreate):
    order_id = await database.execute(
        """INSERT INTO orders (telegram_user_id, telegram_username, venue)
           VALUES (:uid, :uname, :venue) RETURNING id""",
        {"uid": order.telegram_user_id, "uname": order.telegram_username, "venue": order.venue},
    )
    for item in order.items:
        await database.execute(
            "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (:oid, :mid, :qty)",
            {"oid": order_id, "mid": item.menu_item_id, "qty": item.quantity},
        )
    return await _get_order(order_id)

@router.get("/", response_model=list[OrderOut])
async def list_orders(venue: str = None):
    if venue:
        orders = await database.fetch_all(
            "SELECT * FROM orders WHERE venue = :venue ORDER BY created_at DESC",
            {"venue": venue}
        )
    else:
        orders = await database.fetch_all("SELECT * FROM orders ORDER BY created_at DESC")
    result = []
    for order in orders:
        items = await database.fetch_all(
            "SELECT menu_item_id, quantity FROM order_items WHERE order_id = :oid",
            {"oid": order["id"]},
        )
        result.append(OrderOut(
            id=order["id"],
            telegram_user_id=order["telegram_user_id"],
            telegram_username=order["telegram_username"],
            venue=order["venue"],
            status=order["status"],
            items=[OrderItemIn(menu_item_id=i["menu_item_id"], quantity=i["quantity"]) for i in items],
        ))
    return result

class StatusUpdate(BaseModel):
    status: str
    reason: str = ""

@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(order_id: int, body: StatusUpdate):
    order = await database.fetch_one("SELECT * FROM orders WHERE id = :id", {"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    allowed = VALID_TRANSITIONS.get(order["status"], [])
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Cannot move from {order[chr(39)]status{chr(39)]} to {body.status}")
    await database.execute(
        "UPDATE orders SET status = :status WHERE id = :id",
        {"status": body.status, "id": order_id},
    )
    if body.status == "ready":
        await _notify(order["telegram_user_id"], {"telegram_user_id": order["telegram_user_id"], "order_id": order_id, "type": "ready"})
    elif body.status == "cancelled":
        await _notify(order["telegram_user_id"], {"telegram_user_id": order["telegram_user_id"], "order_id": order_id, "type": "cancelled", "reason": body.reason})
    return await _get_order(order_id)

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int):
    return await _get_order(order_id)

async def _notify(user_id: int, payload: dict):
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            await client.post(BOT_NOTIFY_URL, json=payload)
    except Exception:
        pass

async def _get_order(order_id: int):
    order = await database.fetch_one("SELECT * FROM orders WHERE id = :id", {"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    items = await database.fetch_all(
        "SELECT menu_item_id, quantity FROM order_items WHERE order_id = :oid", {"oid": order_id}
    )
    return OrderOut(
        id=order["id"],
        telegram_user_id=order["telegram_user_id"],
        telegram_username=order["telegram_username"],
        venue=order["venue"],
        status=order["status"],
        items=[OrderItemIn(menu_item_id=i["menu_item_id"], quantity=i["quantity"]) for i in items],
    )
