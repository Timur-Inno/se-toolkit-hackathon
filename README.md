# InnoFood - Canteen Bot

A Telegram-based food ordering system for Innopolis University students across 4 venues.

## Demo

*Screenshots coming soon*

## Product context

**End users:** Students and staff at Innopolis University.

**Problem:** Students at Innopolis have no way to browse menus or place orders in advance across the different food venues on campus, causing queues and uncertainty.

**Solution:** A Telegram bot lets students pick a venue, browse today's menu, and place orders instantly. Each venue has its own password-protected admin panel to manage their menu and orders.

## Features

### Implemented

- Telegram bot with 4 venues: Happiness, Neuro Coffee, In Joy, Canteen
- Per-venue menu browsing and ordering via Telegram
- Shopping cart with order confirmation
- Ready notification - bot notifies student when order is ready for pickup
- Cancel with reason - staff picks a reason, student gets notified instantly
- Per-venue admin panel with password login (locked to that venue)
- Menu tab - add/remove daily items by category
- Orders tab - view active orders, mark ready or served, cancel with reason
- History tab - served and cancelled orders archived separately
- Order state machine - strict flow: pending -> ready -> served
- Auto-refresh - Orders tab updates every 5 seconds
- REST API with Swagger docs at /docs
- PostgreSQL persistent storage
- Dockerized - all services start with one command

### Not yet implemented

- Student order history in the bot
- Push notifications for new orders to admin
- Mobile-friendly admin UI improvements

## Usage

**Students:** Open Telegram, find @InnoFood_bot, send /start, pick a venue, browse the menu, add to cart, confirm order. You will get a Telegram message when your order is ready.

**Staff:** Open your venue link, enter your password, manage your menu and orders from the three tabs.

Admin links:

| Venue | URL | Password |
|-------|-----|----------|
| Happiness | http://10.93.25.190:8080/happiness | happy123 |
| Neuro Coffee | http://10.93.25.190:8080/neuro | neuro123 |
| In Joy | http://10.93.25.190:8080/injoy | injoy123 |
| Canteen | http://10.93.25.190:8080/canteen | canteen123 |

## Deployment

**OS:** Ubuntu 24.04

**Requirements:** Docker, Docker Compose, Telegram bot token from @BotFather
```bash
git clone https://github.com/Timur-Inno/se-toolkit-hackathon.git
cd se-toolkit-hackathon
cp .env.example .env
nano .env  # set TELEGRAM_BOT_TOKEN
docker compose up -d
```

| Service | URL |
|---------|-----|
| API | http://10.93.25.190:8000 |
| Swagger docs | http://10.93.25.190:8000/docs |
| Admin panel | http://10.93.25.190:8080/happiness (etc.) |

## Author

Timur Rasulov - SE Toolkit Hackathon 2026
