import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.template.loader import render_to_string

try:
    html = render_to_string('shop/catalog.html', {'results': [], 'categories': [], 'request': None})
    print("✅ Template renders OK (empty data)")
except Exception as e:
    print(f"❌ Template error: {e}")
    import traceback
    traceback.print_exc()
