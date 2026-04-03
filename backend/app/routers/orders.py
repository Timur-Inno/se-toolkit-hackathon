from fastapi import APIRouter, HTTPException
from ..database import database
from ..models.schemas import OrderCreate, OrderOut, OrderItemIn

router = APIRouter()

@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(order: OrderCreate):
    order_id = await database.execute(
        """INSERT INTO orders (telegram_user_id, telegram_username)
           VALUES (:uid, :uname) RETURNING id""",
        {"uid": order.telegram_user_id, "uname": order.telegram_username},
    )
    for item in order.items:
        await database.execute(
            "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (:oid, :mid, :qty)",
            {"oid": order_id, "mid": item.menu_item_id, "qty": item.quantity},
        )
    return await _get_order(order_id)

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int):
    return await _get_order(order_id)

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
        status=order["status"],
        items=[OrderItemIn(menu_item_id=i["menu_item_id"], quantity=i["quantity"]) for i in items],
    )
