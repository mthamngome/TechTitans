import sqlite3

with sqlite3.connect('database.db') as db:
    cursor=db.cursor()
    cursor.execute('''SELECT *  FROM users''')

for db in cursor.fetchall():
    print(db)

