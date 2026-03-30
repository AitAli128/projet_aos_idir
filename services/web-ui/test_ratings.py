import requests
import json

API_URL = 'http://catalog-api:8000/api'

print("=== TEST SYSTEME DE NOTATION ET AUTO-SHIPPING ===\n")

# Test 1: Get products with ratings
print("TEST 1: Produits avec évaluations")
response = requests.get(f'{API_URL}/products/?limit=3')
if response.status_code == 200:
    data = response.json()
    if isinstance(data, dict) and 'results' in data:
        for p in data['results'][:3]:
            print(f"\n{p.get('name')}")
            print(f"  Average Rating: {p.get('average_rating', 0)}⭐")
            print(f"  Your Rating: {p.get('user_rating', 'Not rated')}")
    else:
        print(f"Unexpected format: {type(data)}")
else:
    print(f"Error: {response.status_code}")

# Test 2: Check rating endpoints
print("\n\nTEST 2: Endpoints de notation")
response = requests.get(f'{API_URL}/products/')
if response.status_code == 200:
    data = response.json()
    if isinstance(data, dict) and 'results' in data and data['results']:
        product_id = data['results'][0]['id']
        product_name = data['results'][0]['name']
        
        print(f"Product: {product_name} (ID: {product_id})")
        
        # Try to rate without auth
        print(f"\n  Testing rate endpoint (no auth)...")
        rate_response = requests.post(
            f'{API_URL}/products/{product_id}/rate/',
            json={"score": 5}
        )
        print(f"  Status: {rate_response.status_code} (Expected 401)")
        
        # Try to unrate without auth
        print(f"  Testing unrate endpoint (no auth)...")
        unrate_response = requests.post(
            f'{API_URL}/products/{product_id}/unrate/'
        )
        print(f"  Status: {unrate_response.status_code} (Expected 401)")
        print(f"  Response: {unrate_response.text[:150]}")

print("\n\n✅ Tests d'API complétés!")
print("\nEndpoints disponibles:")
print("  POST /api/products/{id}/rate/ - Évaluer un produit (1-5 étoiles)")
print("  POST /api/products/{id}/unrate/ - Supprimer son évaluation")
print("  GET /api/products/ - Voir les évaluations moyennes et l'évaluation de l'utilisateur")
