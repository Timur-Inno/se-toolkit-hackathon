# Canteen Bot

A Telegram-based canteen ordering system for university students.

## Demo

![Admin UI](https://via.placeholder.com/800x400?text=Admin+UI+screenshot)
![Bot](https://via.placeholder.com/800x400?text=Telegram+Bot+screenshot)

## Product context

**End users:** University students and canteen staff at Innopolis University.

**Problem:** Students have no way to browse the canteen menu or place orders in advance, leading to queues and uncertainty about what's available.

**Solution:** A Telegram bot lets students browse today's menu and place orders instantly. Canteen staff manage the daily menu through a simple web admin panel.

## Features

### Implemented
- Telegram bot: browse today's menu, add items to cart, place order, get confirmation
- Web admin panel: add and remove menu items for today
- REST API: full menu CRUD and order management
- PostgreSQL: persistent storage for menu items and orders
- Dockerized: all services run with a single `docker compose up`

### Not yet implemented
- Order status updates (ready/picked up)
- Authentication for admin panel
- Order history for students
- Push notifications when order is ready

## Usage

**Students:** Open Telegram, find the bot, send `/start`, browse the menu, tap items to add to cart, confirm order.

**Staff:** Open the admin page at `http://SERVER_IP:8080`, add today's menu items with name, price and category.

## Deployment

**OS:** Ubuntu 24.04

**Requirements:**
- Docker + Docker Compose
- A Telegram bot token from @BotFather

**Steps:**
```bash
git clone https://github.com/Timur-Inno/se-toolkit-hackathon.git
cd se-toolkit-hackathon
cp .env.example .env
nano .env  # set TELEGRAM_BOT_TOKEN
docker compose up -d
```

Services:
- API: `http://SERVER_IP:8000`
- Admin: `http://SERVER_IP:8080`
- Docs: `http://SERVER_IP:8000/docs`
