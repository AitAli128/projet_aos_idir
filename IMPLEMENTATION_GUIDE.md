# 🛠️ GUIDE D'IMPLÉMENTATION

## 📋 Étapes d'implémentation

### Phase 1: Préparation
1. Cloner le dépôt
2. Configurer l'environnement
3. Démarrer les services Docker

### Phase 2: Base de données
1. Créer les migrations
2. Appliquer les migrations
3. Peupler les données de démo

### Phase 3: Backend
1. Implémenter les modèles
2. Créer les serializers
3. Développer les vues API
4. Configurer les URLs

### Phase 4: Frontend
1. Mettre à jour les templates
2. Ajouter le JavaScript
3. Tester l'interface

### Phase 5: Tests
1. Tests unitaires
2. Tests d'intégration
3. Tests manuels

## 🗄️ Modèles de données

### ProductLike
```python
class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_like')
        ]
```

### Order (étendu)
```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)
```

## 🔌 Endpoints API

### Likes
- `POST /api/products/{id}/like/` - Like/unlike un produit
- `GET /api/products/{id}/likes/` - Liste des likes

### Commandes
- `POST /api/orders/` - Créer une commande
- `GET /api/orders/` - Liste des commandes
- `GET /api/orders/{id}/` - Détails commande

## 🎨 Frontend Components

### Like Button
```html
<button class="btn btn-sm like-btn" 
        data-product-id="{{ product.id }}"
        onclick="toggleLike(this)">
    <span class="heart">❤️</span>
    <span class="count">{{ product.user_likes }}</span>
</button>
```

### Order Form
```html
<form id="order-form">
    <div class="form-group">
        <label for="phone">Téléphone</label>
        <input type="tel" id="phone" name="phone" required>
    </div>
    <div class="form-group">
        <label for="address">Adresse de livraison</label>
        <textarea id="address" name="shipping_address" required></textarea>
    </div>
    <button type="submit" class="btn btn-primary">Passer commande</button>
</form>
```

## 🧪 Tests

### Test Like System
```python
def test_product_like(self):
    client = APIClient()
    client.force_authenticate(user=self.user)
    
    # Like un produit
    response = client.post('/api/products/1/like/')
    self.assertEqual(response.status_code, 200)
    
    # Vérifier que le like existe
    self.assertTrue(ProductLike.objects.filter(user=self.user, product_id=1).exists())
```

### Test Order Creation
```python
def test_order_creation_with_phone_address(self):
    data = {
        'lines': [{'product_id': 1, 'quantity': 2}],
        'phone': '0123456789',
        'shipping_address': '123 rue de la paix'
    }
    response = self.client.post('/api/orders/', data)
    self.assertEqual(response.status_code, 201)
```

## 🚀 Déploiement

```bash
# Build
docker compose build --no-cache

# Up
docker compose up -d

# Migrate
docker compose exec catalog-api python manage.py migrate

# Test
curl http://localhost:8081/api/products/
```

## ✅ Validation

- [ ] Like/unlike fonctionne
- [ ] Un seul like par utilisateur
- [ ] Commande avec téléphone et adresse
- [ ] Interface responsive
- [ ] Tests passent
