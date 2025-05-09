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


    # ✅ Новая таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            full_name TEXT,
            contact_phone TEXT,
            city TEXT,
            traveler_type TEXT,
            interests TEXT,
            bio TEXT,
            is_registered INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # ✅ Обратная связь по удалению
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deletion_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            reason TEXT,
            deleted_at TEXT
        )
    """)

    #логирование удаленных поездок
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deleted_trips_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            user_id INTEGER,
            username TEXT,
            location TEXT,
            date_from TEXT,
            date_to TEXT,
            purpose TEXT,
            deleted_at TEXT,
            deleted_by TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            payload TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

DB_PATH = "trips.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

# Сохранение поездки
def save_trip(user_id, username, data: dict) -> int:
    insert_dttm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trips (
            user_id, username, country, location,
            date_from, date_to, purpose, companions, description, insert_dttm
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
    # получить последний insert_id
    rowid = cur.lastrowid
    conn.commit()
    conn.close()
    return rowid


def save_user(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO users (
            telegram_id, username, full_name, contact_phone, city,
            traveler_type, interests, bio, gender, birth_year,
            is_registered, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        data["telegram_id"],
        data.get("username"),
        data.get("full_name"),
        data.get("contact_phone"),
        data.get("city"),
        data.get("traveler_type"),
        ",".join(data.get("interests", [])),
        data.get("bio"),
        data.get("gender"),
        data.get("birth_year"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def is_user_registered(telegram_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_registered FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row and row[0])

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
    cur.execute("""
        SELECT 
            rowid, user_id, username, country, location,
            date_from, date_to, purpose, companions,
            description, INSERT_DTTM
        FROM trips
        WHERE user_id = ?
        ORDER BY INSERT_DTTM DESC
    """, (user_id,))
    trips = cur.fetchall()
    conn.close()
    return trips


#удаление поездки по клиенту и id поездки
def delete_trip_by_user(trip_id: int, user_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT rowid, user_id, username, location, date_to, date_from, purpose FROM trips WHERE rowid = ? AND user_id = ?", (trip_id, user_id))
    trip = cur.fetchone()

    if trip:
        log_deleted_trip(trip, "manual")

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
    cursor.execute("""
        SELECT telegram_id, username, full_name, city, traveler_type, interests, bio
        FROM users
        WHERE telegram_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "telegram_id": row[0],
            "username": row[1],
            "full_name": row[2],
            "city": row[3],
            "traveler_type": row[4],
            "interests": row[5],
            "bio": row[6]
        }
    return None


def get_user_profile(telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT full_name, gender, birth_year, city, traveler_type, interests, bio
        FROM users
        WHERE telegram_id = ?
    """, (telegram_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "full_name": row[0],
            "gender": row[1],
            "birth_year": row[2],
            "city": row[3],
            "traveler_type": row[4],
            "interests": row[5],
            "bio": row[6]
        }
    return None


def update_user_field(telegram_id: int, field: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, telegram_id))
    conn.commit()
    conn.close()


def delete_user_and_trips(telegram_id: int):
    conn = get_connection()
    cur = conn.cursor()

    # Логируем все поездки перед удалением
    cur.execute("""
        SELECT rowid, user_id, username, location, date_to, date_from, purpose
        FROM trips
        WHERE user_id = ?
    """, (telegram_id,))
    trips = cur.fetchall()

    for trip in trips:
        log_deleted_trip(trip, "profile_deleted")

    # Удаляем поездки и пользователя
    cur.execute("DELETE FROM trips WHERE user_id = ?", (telegram_id,))
    cur.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))

    conn.commit()
    conn.close()



def save_deletion_feedback(telegram_id: int, username: str, reason: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO deletion_feedback (telegram_id, username, reason, deleted_at)
        VALUES (?, ?, ?, ?)
    """, (
        telegram_id,
        username,
        reason,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

#логгер удаления поездок
def log_deleted_trip(trip: tuple, deleted_by: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO deleted_trips_log (
            trip_id, user_id, username, location, date_from, date_to, purpose,
            deleted_at, deleted_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trip[0],         # rowid
        trip[1],         # user_id
        trip[2],         # username
        trip[3],         # location
        trip[4],         # date_to
        trip[5],         # date_from
        trip[6],         # purpose
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        deleted_by
    ))

    conn.commit()
    conn.close()

def get_trip_by_id(rowid: int):
    """
    Возвращает кортеж из 11 полей для заданного rowid:
    (rowid, user_id, username, country, location,
     date_from, date_to, purpose, companions,
     description, insert_dttm)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            rowid, user_id, username, country, location,
            date_from, date_to, purpose, companions,
            description, insert_dttm
        FROM trips
        WHERE rowid = ?
    """, (rowid,))
    trip = cur.fetchone()
    conn.close()
    return trip


# Добавим три функции работы с уведомлениями в структуре trips.db

def add_notification(user_id: int, type_: str, payload: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, type, payload)
        VALUES (?, ?, ?)
    """, (user_id, type_, payload))
    conn.commit()
    conn.close()

def get_unread_notifications(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type, payload, created_at
        FROM notifications
        WHERE user_id = ? AND is_read = 0
        ORDER BY created_at DESC
    """, (user_id,))
    notifications = cur.fetchall()
    conn.close()
    return notifications

def mark_notification_read(notification_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE id = ?
    """, (notification_id,))
    conn.commit()
    conn.close()


#айдишки уведомлений
def get_all_notifications_by_filter(user_id: int, filter_type: str):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT id, type, payload, is_read, created_at
        FROM notifications
        WHERE user_id = ?
    """
    if filter_type in ("new_join", "joined_by_link", "new_follower", "system"):
        query += " AND type = ?"
        cur.execute(query + " ORDER BY created_at DESC", (user_id, filter_type))
    elif filter_type == "read":
        query += " AND is_read = 1 ORDER BY created_at DESC"
        cur.execute(query, (user_id,))
    elif filter_type == "unread":
        query += " AND is_read = 0 ORDER BY created_at DESC"
        cur.execute(query, (user_id,))
    else:
        query += " ORDER BY created_at DESC"
        cur.execute(query, (user_id,))

    rows = cur.fetchall()
    conn.close()
    return rows

# подсчет количества непрочитанных уведомлений
def count_unread_notifications(user_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count
