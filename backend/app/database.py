import os
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://canteen:canteen@localhost:5432/canteen")
database = Database(DATABASE_URL)
