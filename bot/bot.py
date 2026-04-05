import os
import asyncio
import httpx
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler,
)

API_BASE = os.getenv("API_BASE_URL", "http://backend:8000")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHOOSING_VENUE, BROWSING, CONFIRMING = range(3)

VENUES = {
    "happiness": {"name": "Happiness", "emoji": "🍔", "categories": ["main", "snack", "side", "drink", "dessert"]},
    "neuro":     {"name": "Neuro Coffee", "emoji": "☕", "categories": ["coffee", "latte", "tea", "pastry", "snack"]},
    "injoy":     {"name": "In Joy", "emoji": "🧋", "categories": ["coffee", "latte", "tea", "pastry", "snack"]},
    "canteen":   {"name": "Canteen", "emoji": "🍽", "categories": ["soup", "main", "side", "drink", "dessert"]},
}

tg_app = None

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["cart"] = {}
    ctx.user_data["venue"] = None
    keyboard = [[InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"venue_{k}")]
                for k, v in VENUES.items()]
    await update.message.reply_text(
        "🏪 *Where do you want to order from?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_VENUE

async def choose_venue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    venue_key = query.data.split("_", 1)[1]
    ctx.user_data["venue"] = venue_key
    ctx.user_data["cart"] = {}
    venue = VENUES[venue_key]

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/menu/", params={"venue": venue_key})
        items = resp.json()

    if not items:
        await query.edit_message_text(f"No menu at {venue['name']} today. Check back later!")
        return ConversationHandler.END

    ctx.user_data["menu"] = {str(i["id"]): i for i in items}
    categories = {}
    for item in items:
        categories.setdefault(item["category"], []).append(item)

    text = f"{venue['emoji']} *{venue['name']} - Today's menu*\n\n"
    keyboard = []
    for cat, cat_items in categories.items():
        text += f"*{cat.capitalize()}*\n"
        for item in cat_items:
            text += f"  {item['name']} - {item['price']} R\n"
            keyboard.append([InlineKeyboardButton(
                f"+ {item['name']} ({item['price']} R)",
                callback_data=f"add_{item['id']}"
            )])
        text += "\n"
    keyboard.append([InlineKeyboardButton("🛒 View cart & order", callback_data="cart")])
    keyboard.append([InlineKeyboardButton("🔙 Change venue", callback_data="back_venue")])

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return BROWSING

async def add_to_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.split("_")[1]
    cart = ctx.user_data.setdefault("cart", {})
    cart[item_id] = cart.get(item_id, 0) + 1
    name = ctx.user_data.get("menu", {}).get(item_id, {}).get("name", "item")
    await query.answer(f"Added {name}")
    return BROWSING

async def back_to_venues(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data["cart"] = {}
    keyboard = [[InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"venue_{k}")]
                for k, v in VENUES.items()]
    await query.edit_message_text(
        "🏪 *Where do you want to order from?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_VENUE

async def show_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = ctx.user_data.get("cart", {})
    menu = ctx.user_data.get("menu", {})
    venue_key = ctx.user_data.get("venue", "canteen")
    venue = VENUES.get(venue_key, VENUES["canteen"])

    if not cart:
        await query.edit_message_text("Cart is empty. Use /start to browse.")
        return BROWSING

    total = 0
    text = f"🛒 *Your cart at {venue['name']}:*\n\n"
    for item_id, qty in cart.items():
        item = menu.get(item_id, {})
        subtotal = item.get("price", 0) * qty
        total += subtotal
        text += f"  {item.get('name', '?')} x {qty} = {subtotal:.2f} R\n"
    text += f"\n*Total: {total:.2f} R*"

    keyboard = [
        [InlineKeyboardButton("Confirm order", callback_data="confirm")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMING

async def confirm_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = ctx.user_data.get("cart", {})
    user = query.from_user
    venue_key = ctx.user_data.get("venue", "canteen")
    venue = VENUES.get(venue_key, VENUES["canteen"])

    payload = {
        "telegram_user_id": user.id,
        "telegram_username": user.username,
        "venue": venue_key,
        "items": [{"menu_item_id": int(k), "quantity": v} for k, v in cart.items()],
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/orders/", json=payload)

    if resp.status_code == 201:
        order = resp.json()
        await query.edit_message_text(
            f"{venue['emoji']} *Order #{order['id']} placed at {venue['name']}!*\n\nWe will notify you when it's ready.",
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text("Something went wrong. Try /start again.")

    ctx.user_data["cart"] = {}
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ctx.user_data["cart"] = {}
    await query.edit_message_text("Cancelled. Use /start to begin again.")
    return ConversationHandler.END

async def handle_notify(request):
    data = await request.json()
    user_id = data.get("telegram_user_id")
    order_id = data.get("order_id")
    notify_type = data.get("type", "ready")
    reason = data.get("reason", "")
    if user_id and tg_app:
        if notify_type == "ready":
            msg = f"Your order #{order_id} is ready! Come pick it up."
        else:
            msg = f"Your order #{order_id} has been cancelled."
            if reason:
                msg += f"\n\nReason: {reason}"
            msg += "\n\nSorry for the inconvenience. Use /start to order again."
        await tg_app.bot.send_message(chat_id=user_id, text=msg)
    return web.Response(text="ok")

async def main():
    global tg_app
    web_app = web.Application()
    web_app.router.add_post("/notify", handle_notify)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 9000)
    await site.start()
    print("Notify server running on port 9000")

    tg_app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_VENUE: [
                CallbackQueryHandler(choose_venue, pattern=r"^venue_"),
            ],
            BROWSING: [
                CallbackQueryHandler(add_to_cart, pattern=r"^add_"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
                CallbackQueryHandler(back_to_venues, pattern="^back_venue$"),
            ],
            CONFIRMING: [
                CallbackQueryHandler(confirm_order, pattern="^confirm$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )
    tg_app.add_handler(conv)
    print("Bot started")
    async with tg_app:
        await tg_app.initialize()
        await tg_app.start()
        await tg_app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
