from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'catalog_product'")
print("Product columns:", [row[0] for row in cursor.fetchall()])
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'catalog_order'")
print("Order columns:", [row[0] for row in cursor.fetchall()])
