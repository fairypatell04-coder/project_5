import psycopg2

# -----------------------------
# 1️⃣ Connect to PostgreSQL
# -----------------------------
try:
    conn = psycopg2.connect(
        dbname="orders_db",
        user="postgres",
        password="mypassword",  # <-- Replace with your PostgreSQL password
        host="localhost"
    )
    cur = conn.cursor()
    print("🔹 Connected to orders_db successfully!")
except Exception as e:
    print("❌ Failed to connect to database:", e)
    exit()

# -----------------------------
# 2️⃣ Check if indexes exist
# -----------------------------
try:
    cur.execute("""
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename='orders'
    """)
    indexes = cur.fetchall()
    index_names = [i[0] for i in indexes]

    print("\n🔹 Current indexes on orders table:")
    for idx in indexes:
        print(f"- {idx[0]} : {idx[1]}")

    if "idx_orders_product_name" in index_names:
        print("✅ Index on product_name exists")
    else:
        print("⚠️ Index on product_name is missing!")

except Exception as e:
    print("❌ Error checking indexes:", e)

# -----------------------------
# 3️⃣ CRUD operations
# -----------------------------
try:
    # CREATE
    cur.execute(
        "INSERT INTO orders (product_name, quantity, price) VALUES (%s,%s,%s) RETURNING id",
        ("Laptop", 2, 1000)
    )
    new_id = cur.fetchone()[0]
    print(f"\n✅ Created order ID: {new_id}")

    # READ
    cur.execute("SELECT * FROM orders WHERE id=%s", (new_id,))
    print("🔹 Read order:", cur.fetchone())

    # UPDATE
    cur.execute("UPDATE orders SET price=%s WHERE id=%s", (1200, new_id))
    conn.commit()
    print(f"✅ Updated order ID {new_id} price to 1200")

    # DELETE
    cur.execute("DELETE FROM orders WHERE id=%s", (new_id,))
    conn.commit()
    print(f"✅ Deleted order ID {new_id}")

except Exception as e:
    print("❌ CRUD operation failed:", e)

# -----------------------------
# 4️⃣ Test query performance
# -----------------------------
try:
    cur.execute("EXPLAIN ANALYZE SELECT * FROM orders WHERE product_name='Laptop'")
    query_plan = cur.fetchall()
    print("\n🔹 Query plan for SELECT * WHERE product_name='Laptop':")
    for row in query_plan:
        print(row[0])

except Exception as e:
    print("❌ Error checking query performance:", e)

# -----------------------------
# 5️⃣ Close connection
# -----------------------------
cur.close()
conn.close()
print("\n🔹 Week 3 verification complete ✅")
