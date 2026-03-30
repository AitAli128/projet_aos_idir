from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app='catalog' AND name LIKE '0002%'")
# connection.commit() is not needed in Django shell but doesn't hurt
print("Migration records deleted for catalog matching 0002")
