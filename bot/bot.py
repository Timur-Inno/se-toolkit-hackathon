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
BROWSING, CONFIRMING = range(2)

tg_app = None


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["cart"] = {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/menu/")
        items = resp.json()

    if not items:
        await update.message.reply_text("No menu today yet. Check back later!")
        return ConversationHandler.END

    ctx.user_data["menu"] = {str(i["id"]): i for i in items}
    categories = {}
    for item in items:
        categories.setdefault(item["category"], []).append(item)

    text = "🍽 *Today's menu*\n\n"
    keyboard = []
    for cat, cat_items in categories.items():
        text += f"*{cat.capitalize()}*\n"
        for item in cat_items:
            text += f"  {item['name']} — {item['price']} ₽\n"
            keyboard.append([InlineKeyboardButton(
                f"+ {item['name']} ({item['price']} ₽)",
                callback_data=f"add_{item['id']}"
            )])
        text += "\n"
    keyboard.append([InlineKeyboardButton("🛒 View cart & order", callback_data="cart")])

    await update.message.reply_text(text, parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    return BROWSING


async def add_to_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.split("_")[1]
    cart = ctx.user_data.setdefault("cart", {})
    cart[item_id] = cart.get(item_id, 0) + 1
    name = ctx.user_data.get("menu", {}).get(item_id, {}).get("name", "item")
    await query.answer(f"Added {name} ✓")
    return BROWSING


async def show_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = ctx.user_data.get("cart", {})
    menu = ctx.user_data.get("menu", {})

    if not cart:
        await query.edit_message_text("Cart is empty. Use /start to browse.")
        return BROWSING

    total = 0
    text = "🛒 *Your cart:*\n\n"
    for item_id, qty in cart.items():
        item = menu.get(item_id, {})
        subtotal = item.get("price", 0) * qty
        total += subtotal
        text += f"  {item.get('name', '?')} × {qty} = {subtotal:.2f} ₽\n"
    text += f"\n*Total: {total:.2f} ₽*"

    keyboard = [
        [InlineKeyboardButton("✅ Confirm order", callback_data="confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMING


async def confirm_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = ctx.user_data.get("cart", {})
    user = query.from_user

    payload = {
        "telegram_user_id": user.id,
        "telegram_username": user.username,
        "items": [{"menu_item_id": int(k), "quantity": v} for k, v in cart.items()],
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/orders/", json=payload)

    if resp.status_code == 201:
        order = resp.json()
        await query.edit_message_text(
            f"✅ *Order #{order['id']} placed!*\n\nWe'll notify you when it's ready.",
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
    if user_id and tg_app:
        await tg_app.bot.send_message(
            chat_id=user_id,
            text=f"🔔 *Order #{order_id} is ready!* Come pick it up.",
            parse_mode="Markdown",
        )
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
            BROWSING: [
                CallbackQueryHandler(add_to_cart, pattern=r"^add_"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
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
