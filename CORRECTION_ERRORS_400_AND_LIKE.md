# 📝 CORRECTION ERREURS 400 ET SYSTÈME DE LIKE

## 🐛 Problèmes Corrigés

### Erreur 400 lors de l'ajout de produit
**Cause**: Champ `rating` read-only envoyé lors de la création
**Solution**: Suppression du champ dans le code et template

### Système de like ne fonctionne pas
**Cause**: Erreur dans `product_like()` et gestion d'erreur faible
**Solution**: Amélioration de la gestion d'erreur, ajout payload vide

### Utilisateur peut like plusieurs fois
**Cause**: Pas de système de tracking des likes par utilisateur
**Solution**: Nouveau modèle `ProductLike` avec contrainte unique

## 📞 Ajout Téléphone et Adresse dans Commande

Pour ajouter les champs téléphone et adresse lors de la commande :

### 1. Modèle Order
```python
class Order(models.Model):
    # ... champs existants ...
    phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)
```

### 2. Serializer
```python
class OrderSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)
```

### 3. Template
Ajouter les champs dans le formulaire de commande :
```html
<div class="form-group">
    <label>Téléphone:</label>
    <input type="tel" name="phone" class="form-control">
</div>
<div class="form-group">
    <label>Adresse de livraison:</label>
    <textarea name="shipping_address" class="form-control"></textarea>
</div>
```
