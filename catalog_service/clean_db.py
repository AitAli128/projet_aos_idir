from django.db import connection
cursor = connection.cursor()
tables_columns = {
    'catalog_product': ['expiration_date', 'image_url', 'rating'],
    'catalog_order': ['order_number', 'shipping_address', 'shipping_city', 'shipping_phone']
}
for table, cols in tables_columns.items():
    for col in cols:
        try:
            # We use a sub-transaction or just catch and rollback
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS {col}")
            print(f"Ensured {col} is dropped from {table}")
        except Exception as e:
            print(f"Error dropping {col} from {table}: {e}")
            connection.rollback()
connection.commit()
print("Database cleanup finished.")
