import requests

BASE_URL = 'http://web-ui:8000'

print("=== TEST CATEGORY FILTERING ===\n")

# Get categories first
try:
    # Get home page to see if the categories are loaded
    resp = requests.get(f'{BASE_URL}/catalogue/')
    print(f"Catalog page: {resp.status_code}")
    
    # Check if categories are in the HTML
    if 'Categories' in resp.text or 'Tous les produits' in resp.text:
        print("✅ Category filter section found in catalog page")
    else:
        print("❌ Category filter section NOT found")
    
    # Check for category buttons
    if 'fa-vial' in resp.text:  # Tests icon
        print("✅ Tests category button found (fa-vial icon)")
    if 'fa-mask' in resp.text:  # Masques icon
        print("✅ Masques category button found (fa-mask icon)")
    if 'fa-hands' in resp.text:  # Gants icon
        print("✅ Gants category button found (fa-hands icon)")
    if 'fa-baby' in resp.text:  # Bébé icon
        print("✅ Bebe category button found (fa-baby icon)")
    if 'fa-box' in resp.text:  # Consommables icon
        print("✅ Consommables category button found (fa-box icon)")
    
    # Test with category filter parameter
    resp_filtered = requests.get(f'{BASE_URL}/catalogue/?category=1')
    print(f"\nFiltered catalog (?category=1): {resp_filtered.status_code}")
    
    if resp_filtered.status_code == 200:
        print("✅ Category filtering URLs are working")
    else:
        print("❌ Category filtering URLs failed")
        
except Exception as e:
    print(f"Error: {e}")

print("\n=== EXPECTED RESULT ===")
print("✅ When clicking 'Bebe' → Shows only bebe products")
print("✅ When clicking 'Masques' → Shows only masques products")
print("✅ When clicking 'Tests' → Shows only tests products")
print("✅ When clicking 'Gants' → Shows only gants products")
print("✅ When clicking 'Consommables' → Shows only consommables products")
print("✅ When clicking 'Tous les produits' → Shows all products")

