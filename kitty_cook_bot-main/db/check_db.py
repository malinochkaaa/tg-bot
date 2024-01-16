import sqlite3

path_to_db = "./db/user.db"
connection = sqlite3.connect(path_to_db)
cursor = connection.cursor()

cursor.execute("SELECT * FROM info")
records = cursor.fetchall()
for row in records:
    print(row)

cursor.execute("SELECT * FROM recipes")
records = cursor.fetchall()
for row in records:
    print(row)

cursor.execute("SELECT * FROM rates")
records = cursor.fetchall()
for row in records:
    print(row)

cursor.execute("SELECT * FROM recommendations")
records = cursor.fetchall()
for row in records:
    print(row)
