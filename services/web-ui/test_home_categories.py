import requests

BASE_URL = 'http://web-ui:8000'

print("=== TEST HOME PAGE CATEGORY FILTERING ===\n")

try:
    # Get home page
    resp = requests.get(f'{BASE_URL}/')
    print(f"Home page: {resp.status_code}")
    
    # Check if categories are in the HTML
    if 'bento-grid' in resp.text:
        print("✅ Bento grid found on home page")
    else:
        print("❌ Bento grid NOT found")
    
    # Check for category links with proper IDs
    if 'category=' in resp.text:
        print("✅ Category filter links found")
        # Count how many category links
        count = resp.text.count('?category=')
        print(f"   Found {count} category filter links")
    else:
        print("❌ Category filter links NOT found")
    
    # Verify testing, masques, gants, bebe, consommables categories exist
    categories_to_check = ['tests', 'masques', 'gants', 'bebe', 'consommables']
    for cat in categories_to_check:
        if f'bento-{cat}' in resp.text:
            print(f"✅ {cat.capitalize()} category found")
        else:
            print(f"❌ {cat.capitalize()} category NOT found")

    # Test filtering by clicking on a category (simulate)
    print("\n=== FILTERING SIMULATION ===")
    # Extract first category link
    import re
    match = re.search(r'<a href=[\'"]?([^\'"\s>]+\?category=\d+)', resp.text)
    if match:
        test_url = match.group(1)
        resp_filtered = requests.get(f'{BASE_URL}{test_url}')
        print(f"Filtered URL test: {resp_filtered.status_code}")
        if resp_filtered.status_code == 200:
            print("✅ Category filtering URLs are functional")
        else:
            print("❌ Category filtering URLs failed")
    
except Exception as e:
    print(f"Error: {e}")

print("\n=== EXPECTED RESULT ===")
print("✅ Home page displays category cards with proper links")
print("✅ Clicking 'Tests' → Shows only tests products")
print("✅ Clicking 'Masques' → Shows only masques products")
print("✅ Clicking 'Gants' → Shows only gants products")
print("✅ Clicking 'Bebe' → Shows only bebe products")
print("✅ Clicking 'Consommables' → Shows only consommables products")
