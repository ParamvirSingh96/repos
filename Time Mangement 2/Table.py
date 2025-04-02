import sqlite3

conn = sqlite3.connect(f"hours.db")
cur = conn.cursor()
print("Opened database successfully")

conn.execute('''Create Table Hours
         (DATE      DATE        NOT NULL,
         CATEGORY       TEXT        NOT NULL,
         HOURS      INT     NOT NULL);''')
print("Table created successfully")