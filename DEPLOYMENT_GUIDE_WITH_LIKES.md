# 🚀 GUIDE DE DÉPLOIEMENT - SYSTÈME COMPLET AVEC LIKES

## 📋 Prérequis

- Docker Desktop
- Docker Compose
- Git

## 🐳 Déploiement Complet

### 1. Cloner le dépôt
```bash
git clone https://github.com/nourcherguii/pharm
cd pharm
```

### 2. Configuration
```bash
cp .env.example .env
# Éditer .env si nécessaire
```

### 3. Démarrage
```bash
docker compose down
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

### 4. Migration (attendre 30s)
```bash
docker compose exec catalog-api python manage.py migrate
```

### 5. Création superutilisateur
```bash
docker compose exec auth-service python manage.py createsuperuser
```

## ✅ Vérification

### Services
```bash
docker compose ps
# Tous les services doivent être "Up"
```

### URLs
- **Web**: http://web.localhost:8081
- **API**: http://api.localhost:8081
- **Admin**: http://admin.localhost:8081
- **Auth**: http://auth.localhost:8081

### Tests
```bash
# Test API
curl http://api.localhost:8081/api/products/

# Test Likes
curl -X POST http://api.localhost:8081/api/products/1/like/
```

## 🔧 Configuration Spéciale

### Likes et Recommandations
- Modèle `ProductLike` avec contrainte unique
- Système de recommandations AI
- Interface utilisateur avec toggle like/unlike

### Ajout Téléphone/Adresse
Les champs sont automatiquement ajoutés au formulaire de commande :
- `phone` - Champ téléphone
- `shipping_address` - Adresse de livraison

## 🐨 Dépannage

### Erreur 400 Produit
```bash
docker compose build --no-cache catalog-api
docker compose restart catalog-api
```

### Likes ne fonctionnent pas
```bash
docker compose exec catalog-api python manage.py migrate
docker compose restart web-ui
```

### Base de données vide
```bash
docker compose exec catalog-api python manage.py seed_demo
```
