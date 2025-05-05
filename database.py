import sqlite3
from datetime import date, timedelta, datetime

# Создание подключения и таблицы
def init_db():
    conn = sqlite3.connect("trips.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        country TEXT,        
        location TEXT,
        date_from TEXT,
        date_to TEXT,
        purpose TEXT,
        companions TEXT,
        description TEXT
        )
    """)
    conn.commit()
    conn.close()


DB_PATH = "trips.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# Сохранение поездки
def save_trip(user_id, username, data: dict):
    insert_dttm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.cursor()
    print("Сохраняю:", data)
    cur.execute("""
        INSERT INTO trips (
            user_id, username, country, location,
            date_from, date_to, purpose, companions, description, INSERT_DTTM
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        data.get("country", ""),
        data.get("location", ""),
        data.get("date_from", ""),
        data.get("date_to", ""),
        data.get("purpose", ""),
        data.get("companions", ""),
        data.get("description", ""),
        insert_dttm
    ))
    conn.commit()
    conn.close()


#удаление записей по пользователю
def delete_trips_by_user(user_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM trips WHERE user_id = ?", (user_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted  # вернёт число удалённых строк

#удаление конкретной записи
def delete_trip(trip_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM trips WHERE rowid = ?", (trip_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

#пользователь видит свои поездки
def get_trips_by_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT rowid, location, date_to, date_from, purpose, companions, description FROM trips WHERE user_id = ?", (user_id,))
    trips = cur.fetchall()
    conn.close()
    return trips

#удаление поездки по клиенту и id поездки
def delete_trip_by_user(trip_id: int, user_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM trips WHERE rowid = ? AND user_id = ?", (trip_id, user_id))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


#функция поиска направлений
def search_trips_by_location(query: str):
    query = query.strip().lower()
    print(f"[ПОИСК] Запрос от пользователя: '{query}'")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT rowid, user_id, username, location, date_to, date_from, purpose, companions, description
    FROM trips
    WHERE LOWER(location) LIKE ?
    ORDER BY id DESC
    """, (f"%{query.lower()}%",))
    trips = cur.fetchall()
    conn.close()

    print(f"[ПОИСК] Найдено поездок: {len(trips)}")
    for trip in trips:
        print(f"  → {trip[3]} | дата: {trip[4]} | автор: {trip[2]}")
    
    return trips


#присоединение к поездке
def get_all_trips():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT rowid, user_id, username, location, date_to, date_from, purpose, companions, description
        FROM trips
        ORDER BY id DESC
    """)
    trips = cur.fetchall()
    conn.close()
    return trips


#нормализация хранилища
def normalize_locations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT rowid, location FROM trips")
    rows = cur.fetchall()

    for rowid, location in rows:
        normalized = location.strip().lower()
        cur.execute("UPDATE trips SET location = ? WHERE rowid = ?", (normalized, rowid))

    conn.commit()
    conn.close()
    print("[НОРМАЛИЗАЦИЯ] Завершена успешно.")





def get_trips_by_date_category(category: str):
    today = date.today()
    conn = get_connection()
    cur = conn.cursor()

    if category == "today":
        cur.execute("SELECT * FROM trips WHERE date_to = ?", (today.strftime("%d.%m.%Y"),))
    elif category == "tomorrow":
        d = today + timedelta(days=1)
        cur.execute("SELECT * FROM trips WHERE date_to = ?", (d.strftime("%d.%m.%Y"),))
    elif category == "this_month":
        cur.execute("SELECT * FROM trips WHERE strftime('%m', date_to) = ?", (today.strftime("%m"),))
    elif category == "next_month":
        next_month = today.replace(day=1) + timedelta(days=32)
        cur.execute("SELECT * FROM trips WHERE strftime('%m', date_to) = ?", (next_month.strftime("%m"),))
    elif category == "weekend":
        saturday = today + timedelta((5 - today.weekday()) % 7)
        sunday = saturday + timedelta(days=1)
        cur.execute("SELECT * FROM trips WHERE date_to IN (?, ?)", (
            saturday.strftime("%d.%m.%Y"), sunday.strftime("%d.%m.%Y")
        ))
    elif category == "flexible":
        end_of_year = date(today.year, 12, 31)
        cur.execute("SELECT * FROM trips WHERE date_to >= ? AND date_to <= ?", (
            today.strftime("%d.%m.%Y"), end_of_year.strftime("%d.%m.%Y")
        ))
    else:
        cur.close()
        conn.close()
        return []

    trips = cur.fetchall()
    cur.close()
    conn.close()
    return trips

import sqlite3
import random

def get_trips_by_purpose(purpose: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips WHERE LOWER(purpose) = ?", (purpose.lower(),))
    trips = cur.fetchall()
    conn.close()
    return trips

def get_trips_by_companions(companions: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips WHERE LOWER(companions) = ?", (companions.lower(),))
    trips = cur.fetchall()
    conn.close()
    return trips

def get_trips_by_location_keyword(keyword: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips WHERE LOWER(location) LIKE ?", (f"%{keyword.lower()}%",))
    trips = cur.fetchall()
    conn.close()
    return trips

def get_random_trips(limit=3):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips ORDER BY RANDOM() LIMIT ?", (limit,))
    trips = cur.fetchall()
    conn.close()
    return trips

def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, first_name, last_name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "username": row[1],
            "first_name": row[2],
            "last_name": row[3]
        }
    return None
