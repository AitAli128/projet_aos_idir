# ⚡ FIX ULTRA-RAPIDE (2 minutes)

## 🐛 Votre Problème
❌ Ajouter produit dans admin ne marche pas (Erreur 400)
❌ Like système ne fonctionne pas
❌ Manque téléphone et adresse dans la commande

## 🚀 Solution (Copier-Coller)

```bash
cd c:\Users\hiche\pharm

# 1. Arrêter
docker compose down

# 2. Nettoyer
docker system prune -f

# 3. Reconstruire (IMPORTANT: --no-cache)
docker compose build --no-cache catalog-api web-ui

# 4. Démarrer
docker compose up -d

# 5. TRÈS IMPORTANT: Attendre 30 secondes, puis:
docker compose exec catalog-api python manage.py migrate

# 6. Vérifier
docker compose ps
```

## ✅ Tests Immédiats

### Test 1: Ajouter Produit
1. Allez → http://admin.localhost:8081/admin/
2. Connectez-vous avec `admin@demo.local` / `adminadmin123`
3. Allez à Produits > Add Produit
4. Remplissez les champs (SAUF rating)
5. ✅ Doit fonctionner sans erreur 400

### Test 2: Like Produit
1. Allez → http://web.localhost:8081/shop/catalogue/
2. Cliquez sur ❤️ sur un produit
3. ✅ Doit afficher "Merci pour votre recommandation"
4. Recliquez → ✅ Doit afficher "Recommandation retirée"

### Test 3: Commande avec Téléphone/Adresse
1. Ajoutez des produits au panier
2. Allez au panier → Commander
3. ✅ Doit afficher les champs téléphone et adresse
4. Remplissez et validez

## 🎉 Terminé !

Si erreur → Consultez **FIX_NOW.md**

**Note**: Les champs téléphone et adresse sont maintenant automatiquement inclus dans le formulaire de commande !
