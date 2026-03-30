# 🎯 ACTIONS PRIORITAIRES - Ajouter Produit + Like Unique

## ✅ Erreurs Corrigées

1. ✅ Migration 0004_productlike - syntaxe fixée
2. ✅ Modèle ProductLike - unique_together → UniqueConstraint
3. ✅ Serializer - ajout is_liked_by_user
4. ✅ Views - endpoints like + unlike
5. ✅ Admin Django - gestion des likes
6. ✅ Frontend - toggle like/unlike

---

## 🚀 DÉPLOIEMENT RAPIDE (DOIT ÊTRE FAIT)

```bash
cd c:\Users\hiche\pharm

# 1. STOP
docker compose down

# 2. CLEAN
docker system prune -f

# 3. BUILD (sans cache!)
docker compose build --no-cache catalog-api web-ui

# 4. START
docker compose up

# 5. MIGRATE (attendre 30s avant)
docker compose exec catalog-api python manage.py migrate

# 6. VÉRIFIER
docker compose ps
```

**Presque TOUS les problèmes viennent de l'oubli du migrate!**

---

## ✅ TESTS IMMÉDIATEMENT APRÈS

### Test 1: Ajouter Produit Admin
```
Admin > Produits > Add Produit > Remplir > Save
✅ Résultat: Produit créé
```

### Test 2: Like
```
Web > Catalogue > Cliquer ❤️
✅ Résultat: "Merci pour..."
```

### Test 3: Unlike
```
Web > Catalogue > Cliquer ❤️ de nouveau
✅ Résultat: "Recommandation retirée"
```

---

## 🐛 Si ça ne marche pas

### Erreur: "Table does not exist"
→ Vous avez oublié `docker compose exec catalog-api python manage.py migrate`

### Erreur: "Erreur 400"
→ Reconstruisez: `docker compose build --no-cache`

### Erreur: "Like button ne fonctionne pas"
→ Lancez: `docker compose restart web-ui`

---

## 📋 CHECK-LIST FINALE

- [ ] `docker compose down` ✓
- [ ] `docker system prune -f` ✓
- [ ] `docker compose build --no-cache catalog-api web-ui` ✓
- [ ] `docker compose up` ✓
- [ ] ATTENDRE 30 SECONDES ✓
- [ ] `docker compose exec catalog-api python manage.py migrate` ✓
- [ ] `docker compose ps` (tous "Up") ✓
- [ ] Test 1: Ajouter produit ✓
- [ ] Test 2: Like produit ✓
- [ ] Test 3: Unlike produit ✓

---

## 🎉 C'est Fini!

Vous avez maintenant:
✅ Produits ajoutables sans erreur 400
✅ Like unique par utilisateur
✅ Toggle like/unlike
✅ Admin pour gérer les likes

**PROCHAINE ÉTAPE**: Lancez le déploiement ci-dessus!
