import requests
import json

API_URL = 'http://catalog-api:8000/api'

# Test endpoint for products
try:
    response = requests.get(f'{API_URL}/products/?limit=5')
    print('=== PRODUITS (API) ===')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            for p in data['results'][:3]:
                print(f"\n{p.get('name')}")
                print(f"  Recommandations: {p.get('user_recommendations', 0)}")
                print(f"  Likes: {p.get('user_likes', 0)}")
                print(f"  is_recommended_by_user: {p.get('is_recommended_by_user', False)}")
                print(f"  is_liked_by_user: {p.get('is_liked_by_user', False)}")
        else:
            print(f'Response type: {type(data)}, Keys: {list(data.keys()) if isinstance(data, dict) else "list"}')
            # print first 2 items
            print(json.dumps(str(data[:2]), indent=2))
    else:
        print(f'Error: {response.status_code} - {response.text}')
except Exception as e:
    print(f'Error: {e}')
