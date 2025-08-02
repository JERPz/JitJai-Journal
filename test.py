import psycopg2

try:
    conn = psycopg2.connect(
        host="db.rslbfdbptsmcjpimgucx.supabase.co",
        database="postgres",
        user="postgres",
        password="your_password",
        port=5432
    )
    print("Connected!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
