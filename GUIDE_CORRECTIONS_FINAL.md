# 🔧 GUIDE FINAL DES CORRECTIONS

## 🎯 Objectifs

Ce guide contient toutes les corrections finales pour :
- ✅ Résoudre les erreurs 400 lors de l'ajout de produits
- ✅ Implémenter un système de like fonctionnel
- ✅ Ajouter téléphone et adresse dans les commandes
- ✅ Améliorer l'interface utilisateur

## 📋 Checklist des Corrections

### 1. Backend - Models
```python
# services/catalog-api/apps/catalog/models.py
class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_like')
        ]

class Order(models.Model):
    # ... champs existants ...
    phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)
```

### 2. Backend - Serializers
```python
# services/catalog-api/apps/catalog/serializers.py
class ProductSerializer(serializers.ModelSerializer):
    is_liked_by_user = serializers.SerializerMethodField()
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProductLike.objects.filter(user=request.user, product=obj).exists()
        return False

class OrderSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)
```

### 3. Backend - Views
```python
# services/catalog-api/apps/catalog/views.py
class ProductLikeView(APIView):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        like, created = ProductLike.objects.get_or_create(user=request.user, product=product)
        if not created:
            like.delete()
            return Response({"message": "Like retiré"})
        return Response({"message": "Produit liké"})
```

### 4. Frontend - Templates
```html
<!-- services/web-ui/templates/shop/catalog.html -->
<button class="btn btn-sm {% if product.is_liked_by_user %}btn-danger{% else %}btn-outline-danger{% endif %}" 
        onclick="toggleLike({{ product.id }})">
    ❤️ {{ product.user_likes }}
</button>

<script>
function toggleLike(productId) {
    fetch(`/api/products/${productId}/like/`, {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')}
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    });
}
</script>
```

### 5. Formulaire Commande
```html
<!-- services/web-ui/templates/shop/checkout.html -->
<div class="row">
    <div class="col-md-6">
        <div class="form-group">
            <label for="phone">Téléphone *</label>
            <input type="tel" id="phone" name="phone" class="form-control" required>
        </div>
    </div>
    <div class="col-md-6">
        <div class="form-group">
            <label for="email">Email *</label>
            <input type="email" id="email" name="email" class="form-control" required>
        </div>
    </div>
</div>
<div class="form-group">
    <label for="address">Adresse de livraison *</label>
    <textarea id="address" name="shipping_address" class="form-control" rows="3" required></textarea>
</div>
```

## 🚀 Déploiement

```bash
# 1. Arrêter les services
docker compose down

# 2. Nettoyer
docker system prune -f

# 3. Reconstruire
docker compose build --no-cache catalog-api web-ui

# 4. Démarrer
docker compose up -d

# 5. Migration (attendre 30s)
docker compose exec catalog-api python manage.py migrate

# 6. Vérifier
docker compose ps
```

## ✅ Tests Finaux

1. **Admin**: Ajouter produit sans erreur 400
2. **Like**: Cliquer ❤️ sur un produit
3. **Commande**: Remplir téléphone et adresse
4. **Recommandation**: Système de recommandations AI

Toutes les corrections sont maintenant appliquées !
