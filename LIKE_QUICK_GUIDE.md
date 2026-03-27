# ⚡ GUIDE RAPIDE - SYSTÈME DE LIKE

## 🎯 Fonctionnement

### Like/Unlike
- **Like**: `POST /api/products/{id}/like/`
- **Unlike**: `POST /api/products/{id}/unlike/`
- **Toggle**: Même endpoint, détecte automatiquement

### Frontend
```javascript
function toggleLike(productId) {
    fetch(`/api/products/${productId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Mettre à jour l'interface
        location.reload();
    });
}
```

### Backend
```python
class ProductLikeView(APIView):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        like, created = ProductLike.objects.get_or_create(
            user=request.user, 
            product=product
        )
        if not created:
            like.delete()
            return Response({"message": "Like retiré"})
        return Response({"message": "Produit liké"})
```

## 🔄 Déploiement

```bash
docker compose exec catalog-api python manage.py migrate
docker compose restart web-ui
```

## ✅ Test

1. Allez sur http://web.localhost:8081/shop/catalogue/
2. Cliquez sur ❤️
3. Vérifiez le message "Merci pour votre recommandation"
4. Recliquez pour unlike
