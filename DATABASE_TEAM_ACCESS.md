# 🗄️ ACCÈS BASE DE DONNÉES - ÉQUIPE

## 📋 Informations de Connexion

### Base de données principale
- **Nom**: pharm_db
- **Hôte**: postgres-catalog
- **Port**: 5432
- **Utilisateur**: postgres
- **Mot de passe**: postgres123

### Base de données auth
- **Nom**: auth_db
- **Hôte**: postgres-auth
- **Port**: 5432
- **Utilisateur**: postgres
- **Mot de passe**: postgres123

## 🔐 Accès Équipe

### Développeurs
- **Outils**: pgAdmin, DBeaver, ou psql
- **Permissions**: Lecture/Écriture sur les tables de développement
- **Backup**: Sauvegardes quotidiennes automatiques

### Administrateurs
- **Accès complet**: Toutes les bases de données
- **Permissions**: DROP, ALTER, CREATE
- **Monitoring**: Accès aux logs et métriques

## 📊 Tables Principales

### Catalogue
- `products` - Produits
- `categories` - Catégories
- `orders` - Commandes
- `order_lines` - Lignes de commande
- `product_ratings` - Évaluations
- `product_likes` - Likes

### Authentification
- `users` - Utilisateurs
- `user_profiles` - Profils utilisateurs

## 🔄 Commandes Utiles

```bash
# Connexion psql
docker compose exec postgres-catalog psql -U postgres -d pharm_db

# Backup
docker compose exec postgres-catalog pg_dump -U postgres pharm_db > backup.sql

# Restore
docker compose exec -T postgres-catalog psql -U postgres pharm_db < backup.sql
```
