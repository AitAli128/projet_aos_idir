import requests
import json

API_URL = 'http://catalog-api:8000/api'

# Test product detail
print("=== TEST RECOMMANDATION API ===\n")

# Get first product
response = requests.get(f'{API_URL}/products/')
if response.status_code == 200:
    data = response.json()
    if isinstance(data, dict) and 'results' in data:
        products = data['results']
        if products:
            product_id = products[0]['id']
            print(f"Product: {products[0]['name']} (ID: {product_id})")
            print(f"Current recommendations: {products[0]['user_recommendations']}")
            
            # Test recommend endpoint (without auth - will fail, but tests endpoint exists)
            print(f"\nTesting recommend endpoint...")
            recommend_response = requests.post(
                f'{API_URL}/products/{product_id}/recommend/',
                json={"action": "toggle"},
                headers={'Authorization': 'Bearer invalid_token'}
            )
            print(f"Status: {recommend_response.status_code}")
            print(f"Response: {recommend_response.text[:200]}")
            
            # Test like endpoint
            print(f"\nTesting like endpoint...")
            like_response = requests.post(
                f'{API_URL}/products/{product_id}/like/',
                headers={'Authorization': 'Bearer invalid_token'}
            )
            print(f"Status: {like_response.status_code}")
            print(f"Response: {like_response.text[:200]}")
            
            # Test unlike endpoint
            print(f"\nTesting unlike endpoint...")
            unlike_response = requests.post(
                f'{API_URL}/products/{product_id}/unlike/',
                headers={'Authorization': 'Bearer invalid_token'}
            )
            print(f"Status: {unlike_response.status_code}")
            print(f"Response: {unlike_response.text[:200]}")
else:
    print(f"Error fetching products: {response.status_code}")
