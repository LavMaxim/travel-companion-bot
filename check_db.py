import sqlite3

conn = sqlite3.connect("trips.db")
cur = conn.cursor()

cur.execute("SELECT * FROM trips")
rows = cur.fetchall()

print("📦 Содержимое таблицы trips:")
for row in rows:
    print(row)

conn.close()
