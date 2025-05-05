import sqlite3
import random

locations = ["Москва", "Стамбул", "Бали", "Бангкок", "Дубай", "Сочи", "Ереван", "Барселона", "Рим", "Париж"]
purposes = ["отдых", "работа", "приключения", "свадьба", "переезд"]
companions = ["1-2 человека", "группа", "только девушки", "вдвоём", "не важно"]
descriptions = ["Хочу расслабиться", "Готов к приключениям", "Удалёнка и море", "Нужен напарник", "Всё спланировано"]

def seed_trips():
    conn = sqlite3.connect("trips.db")
    cur = conn.cursor()

    for i in range(15):
        user_id = random.randint(100000, 999999)
        username = f"user{i}"
        location = random.choice(locations)
        date = f"{random.randint(1,28)}.{random.randint(5,12)}.2025"
        purpose = random.choice(purposes)
        companion = random.choice(companions)
        description = random.choice(descriptions)

        cur.execute("""
            INSERT INTO trips (user_id, username, location, date, purpose, companions, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, location, date, purpose, companion, description))

    conn.commit()
    conn.close()
    print("✅ Добавлено 15 тестовых записей в базу.")

if __name__ == "__main__":
    seed_trips()
