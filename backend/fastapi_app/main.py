from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "app.db")

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price REAL,
        seller TEXT,
        image_url TEXT,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        link TEXT
    )
    """)
    # Seed data if empty
    cur.execute("SELECT COUNT(*) as c FROM products")
    if cur.fetchone()["c"] == 0:
        cur.executemany("""
        INSERT INTO products (title, price, seller, image_url, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, [
            ("Handcrafted Textiles", 799, "Lakshmi's Boutique", None, datetime.utcnow().isoformat()),
            ("Traditional Jewelry", 499, "Radha's Creations", None, datetime.utcnow().isoformat()),
            ("Organic Spices Kit", 349, "Meera's Farm", None, datetime.utcnow().isoformat()),
        ])
    cur.execute("SELECT COUNT(*) as c FROM schemes")
    if cur.fetchone()["c"] == 0:
        cur.executemany("""
        INSERT INTO schemes (title, description, link) VALUES (?, ?, ?)
        """, [
            ("Mahila Coir Yojana", "For entrepreneurs running small businesses with 50% firm ownership. Requires completion of EDP programs.", None),
            ("Annapurna Yojana", "Financial aid for establishing food catering units. Requires guarantor and collateral.", None),
            ("Cent Kalyani Scheme", "Central Bank scheme for new ventures, professionals, and self-employed women in various sectors.", None),
            ("Stree Shakti Package", "For women in manufacturing, agriculture, and retail sectors with concessional interest rates.", None),
            ("Udyogini Scheme", "Financial assistance for new industrial ventures in small scale sector.", None),
            ("PSB Schemes", "Punjab and Sind Bank scheme for women in agriculture, retail, and small business.", None),
        ])
    conn.commit()
    conn.close()

class ContactIn(BaseModel):
    name: constr(min_length=1, max_length=120)
    email: EmailStr
    message: constr(min_length=1, max_length=5000)

class SubscribeIn(BaseModel):
    email: EmailStr

class ProductOut(BaseModel):
    id: int
    title: str
    price: Optional[float] = None
    seller: Optional[str] = None
    image_url: Optional[str] = None

class SchemeOut(BaseModel):
    id: int
    title: str
    description: str
    link: Optional[str] = None

app = FastAPI(title="SakhiSetu Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your front-end origin for production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    init_db()

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/products", response_model=List[ProductOut])
def list_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, seller, image_url FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/schemes", response_model=List[SchemeOut])
def list_schemes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, link FROM schemes ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/contact")
def submit_contact(payload: ContactIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contacts (name, email, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (payload.name.strip(), payload.email, payload.message.strip(), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Contact request received"}

@app.post("/api/subscribe")
def subscribe(payload: SubscribeIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO subscribers (email, created_at)
            VALUES (?, ?)
        """, (payload.email, datetime.utcnow().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        # duplicate
        conn.close()
        return {"message": "You are already subscribed"}
    conn.close()
    return {"message": "Subscribed"}
# You can run with: uvicorn fastapi_app.main:app --reload --port 8000
