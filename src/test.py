import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123",
        port="5432"
    )

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM v_line_summary LIMIT 5;")
    result = cursor.fetchone()

    print("Connection successful!")
    print(result)
    print(cursor.fetchall)
    cursor.close()
    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)