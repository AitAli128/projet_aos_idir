# 🔒 SYSTÈME DE LIKE UNIQUE

## 📋 Concept

Chaque utilisateur peut like un produit **une seule fois**. Le système utilise une contrainte de base de données pour garantir l'unicité.

## 🗄️ Modèle

```python
class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], 
                name='unique_user_product_like'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"
```

## 🔌 API Endpoints

### Toggle Like
```python
class ProductLikeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        
        # Tente de créer un like
        like, created = ProductLike.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            # Like existe déjà → le supprimer
            like.delete()
            return Response({
                "message": "Recommandation retirée",
                "liked": False,
                "likes_count": ProductLike.objects.filter(product=product).count()
            })
        
        # Like créé avec succès
        return Response({
            "message": "Merci pour votre recommandation !",
            "liked": True,
            "likes_count": ProductLike.objects.filter(product=product).count()
        })
```

### Serializer avec état du like
```python
class ProductSerializer(serializers.ModelSerializer):
    is_liked_by_user = serializers.SerializerMethodField()
    user_likes = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'is_liked_by_user', 'user_likes']
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return ProductLike.objects.filter(user=request.user, product=obj).exists()
        return False
    
    def get_user_likes(self, obj):
        return ProductLike.objects.filter(product=obj).count()
```

## 🎨 Frontend Implementation

### Template
```html
<div class="product-actions">
    <button class="btn {% if product.is_liked_by_user %}btn-danger{% else %}btn-outline-danger{% endif %}" 
            onclick="toggleLike({{ product.id }})">
        <span class="heart">❤️</span>
        <span class="count">{{ product.user_likes }}</span>
    </button>
</div>
```

### JavaScript
```javascript
async function toggleLike(productId) {
    try {
        const response = await fetch(`/api/products/${productId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Mettre à jour le bouton
            const button = document.querySelector(`[onclick="toggleLike(${productId})"]`);
            const countSpan = button.querySelector('.count');
            
            countSpan.textContent = data.likes_count;
            
            if (data.liked) {
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-danger');
            } else {
                button.classList.remove('btn-danger');
                button.classList.add('btn-outline-danger');
            }
            
            // Afficher le message
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors du like');
    }
}

// Helper pour obtenir le CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

## 🔄 URLs Configuration

```python
# urls.py
urlpatterns = [
    path('products/<int:pk>/like/', ProductLikeView.as_view(), name='product-like'),
    path('products/', ProductListView.as_view(), name='product-list'),
]
```

## ✅ Tests

```python
class ProductLikeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.product = Product.objects.create(name='Test', price=10)
    
    def test_unique_like(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        # Premier like
        response1 = client.post(f'/api/products/{self.product.id}/like/')
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.data['liked'])
        
        # Deuxième like (devrait retirer)
        response2 = client.post(f'/api/products/{self.product.id}/like/')
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(response2.data['liked'])
        
        # Vérifier qu'il n'y a qu'un seul like au maximum
        self.assertEqual(ProductLike.objects.filter(user=self.user, product=self.product).count(), 0)
```

## 🚀 Déploiement

```bash
# Migration de la contrainte unique
docker compose exec catalog-api python manage.py migrate

# Redémarrer les services
docker compose restart catalog-api web-ui
```

Le système garantit maintenant qu'un utilisateur ne peut like un produit qu'une seule fois !
