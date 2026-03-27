# 🎯 RÉSUMÉ - SYSTÈME DE RECOMMANDATIONS

## 🤖 Intelligence Artificielle

### Algorithme de Recommandation
```python
class AIRecommendationEngine:
    def recommend_products(self, user, limit=10):
        """
        Génère des recommandations basées sur:
        - Historique d'achats
        - Produits likés
        - Catégories préférées
        - Produits similaires
        """
        
        # 1. Basé sur les likes de l'utilisateur
        liked_categories = ProductLike.objects.filter(
            user=user
        ).values_list('product__category', flat=True).distinct()
        
        # 2. Produits similaires aux produits likés
        similar_products = self.get_similar_products(user)
        
        # 3. Produits populaires dans les catégories préférées
        popular_in_categories = Product.objects.filter(
            category__in=liked_categories
        ).annotate(
            like_count=Count('likes')
        ).order_by('-like_count')[:limit]
        
        # 4. Fusion et pondération des résultats
        recommendations = self.merge_recommendations(
            similar_products, 
            popular_in_categories
        )
        
        return recommendations[:limit]
    
    def get_similar_products(self, user):
        """Trouve des produits similaires basés sur les likes"""
        user_likes = ProductLike.objects.filter(user=user)
        
        similar_products = []
        for like in user_likes:
            # Produits likés par les mêmes utilisateurs
            other_users_likes = ProductLike.objects.filter(
                product=like.product
            ).exclude(user=user)
            
            for other_like in other_users_likes:
                # Trouver d'autres produits likés par ces utilisateurs
                similar = ProductLike.objects.filter(
                    user=other_like.user
                ).exclude(product=like.product).exclude(user=user)
                
                similar_products.extend([p.product for p in similar])
        
        return list(set(similar_products))
```

## 🎯 Types de Recommandations

### 1. "Parce que vous avez aimé"
```python
def get_because_you_liked_recommendations(user, limit=5):
    """
    Basé sur les produits que l'utilisateur a likés
    """
    user_likes = ProductLike.objects.filter(user=user).select_related('product')
    
    recommendations = []
    for like in user_likes:
        # Trouver des produits similaires
        similar = Product.objects.filter(
            category=like.product.category
        ).exclude(id=like.product.id)
        
        recommendations.extend(similar)
    
    return recommendations[:limit]
```

### 2. "Populaire dans votre catégorie"
```python
def get_popular_in_category_recommendations(user, limit=5):
    """
    Produits populaires dans les catégories préférées de l'utilisateur
    """
    user_categories = ProductLike.objects.filter(
        user=user
    ).values_list('product__category', flat=True).distinct()
    
    popular_products = Product.objects.filter(
        category__in=user_categories
    ).annotate(
        like_count=Count('likes'),
        order_count=Count('orderline')
    ).order_by('-like_count', '-order_count')[:limit]
    
    return popular_products
```

### 3. "Les clients ont aussi acheté"
```python
def get_customers_also_bought_recommendations(user, product_id, limit=5):
    """
    Basé sur les achats des autres clients
    """
    # Clients qui ont acheté ce produit
    customer_orders = OrderLine.objects.filter(
        product_id=product_id
    ).values_list('order__user', flat=True).distinct()
    
    # Autres produits achetés par ces clients
    other_products = OrderLine.objects.filter(
        order__user__in=customer_orders
    ).exclude(product_id=product_id).values('product').annotate(
        purchase_count=Count('product')
    ).order_by('-purchase_count')[:limit]
    
    product_ids = [p['product'] for p in other_products]
    return Product.objects.filter(id__in=product_ids)
```

## 🎨 Interface Utilisateur

### Section Recommandations
```html
<div class="recommendations-section">
    <h3>🎯 Recommandations pour vous</h3>
    
    <div class="recommendation-tabs">
        <button class="tab-btn active" data-tab="because-you-liked">
            Parce que vous avez aimé
        </button>
        <button class="tab-btn" data-tab="popular">
            Populaire dans vos catégories
        </button>
        <button class="tab-btn" data-tab="also-bought">
            Les clients ont aussi acheté
        </button>
    </div>
    
    <div class="recommendation-content">
        <div id="because-you-liked" class="tab-content active">
            {% for product in because_you_liked %}
            {% include 'shop/product_card.html' %}
            {% endfor %}
        </div>
        
        <div id="popular" class="tab-content">
            {% for product in popular_in_categories %}
            {% include 'shop/product_card.html' %}
            {% endfor %}
        </div>
        
        <div id="also-bought" class="tab-content">
            {% for product in customers_also_bought %}
            {% include 'shop/product_card.html' %}
            {% endfor %}
        </div>
    </div>
</div>
```

### API Endpoint
```python
class ProductRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        engine = AIRecommendationEngine()
        
        recommendations = {
            'because_you_liked': engine.get_because_you_liked_recommendations(user),
            'popular_in_categories': engine.get_popular_in_category_recommendations(user),
            'customers_also_bought': engine.get_customers_also_bought_recommendations(user)
        }
        
        # Serializer les produits
        serialized = {}
        for key, products in recommendations.items():
            serialized[key] = ProductSerializer(products, many=True, context={'request': request}).data
        
        return Response(serialized)
```

## 📊 Analytics et Performance

### Tracking des Recommandations
```python
class RecommendationClick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=50)
    clicked_at = models.DateTimeField(auto_now_add=True)
    converted_to_order = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'clicked_at']),
            models.Index(fields=['recommendation_type']),
        ]

def track_recommendation_click(user, product, recommendation_type):
    RecommendationClick.objects.create(
        user=user,
        product=product,
        recommendation_type=recommendation_type
    )
```

### Performance Metrics
```python
def get_recommendation_performance():
    """
    Calcule les métriques de performance du système de recommandation
    """
    clicks = RecommendationClick.objects.all()
    
    metrics = {
        'total_clicks': clicks.count(),
        'conversion_rate': clicks.filter(converted_to_order=True).count() / clicks.count(),
        'clicks_by_type': clicks.values('recommendation_type').annotate(count=Count('id')),
        'top_performing_products': clicks.values('product__name').annotate(count=Count('id')).order_by('-count')[:10]
    }
    
    return metrics
```

## 🤖 Machine Learning (Optionnel)

### TensorFlow/Scikit-learn Integration
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MLRecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.product_matrix = None
    
    def train(self):
        """
        Entraîne le modèle sur les descriptions et catégories des produits
        """
        products = Product.objects.all()
        
        # Créer le corpus de textes
        corpus = []
        for product in products:
            text = f"{product.name} {product.description} {product.category.name}"
            corpus.append(text)
        
        # Vectoriser
        self.product_matrix = self.vectorizer.fit_transform(corpus)
    
    def get_similar_products(self, product_id, limit=10):
        """
        Trouve des produits similaires basés sur le contenu
        """
        if self.product_matrix is None:
            self.train()
        
        product_idx = product_id - 1  # Simplifié
        similarities = cosine_similarity(
            self.product_matrix[product_idx:product_idx+1], 
            self.product_matrix
        ).flatten()
        
        # Trier et retourner les plus similaires
        similar_indices = similarities.argsort()[::-1][1:limit+1]
        
        return Product.objects.filter(id__in=similar_indices + 1)
```

## ✅ Tests

```python
class RecommendationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'test')
        self.category = Category.objects.create(name='Médicaments')
        
        # Créer des produits
        self.product1 = Product.objects.create(name='Produit A', category=self.category)
        self.product2 = Product.objects.create(name='Produit B', category=self.category)
        
        # User like le produit 1
        ProductLike.objects.create(user=self.user, product=self.product1)
    
    def test_because_you_liked_recommendations(self):
        engine = AIRecommendationEngine()
        recommendations = engine.get_because_you_liked_recommendations(self.user)
        
        self.assertIn(self.product2, recommendations)
    
    def test_recommendation_api(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        response = client.get('/api/recommendations/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('because_you_liked', response.data)
```

## 🚀 Déploiement

```bash
# Migration des modèles de recommandation
docker compose exec catalog-api python manage.py migrate

# Collecter les données pour l'entraînement
docker compose exec catalog-api python manage.py collect_recommendation_data

# Tests
docker compose exec catalog-api python manage.py test recommendations
```

## 📋 Checklist

- [ ] Moteur de recommandation basique
- [ ] API endpoints
- [ ] Interface utilisateur
- [ ] Tracking des clics
- [ ] Analytics dashboard
- [ ] Tests complets
- [ ] Documentation utilisateur
