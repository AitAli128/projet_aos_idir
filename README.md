# Marketplace pharmacie (style MarketPharm) — architecture microservices

Projet de démonstration : UI proche d’une marketplace B2B type [MarketPharm](https://marketpharm.fr/) (catalogue pro, panier, remises volume), avec les contraintes **API REST**, **JWT + rôles**, **UI qui consomme l’API**, **RabbitMQ**, **Consul**, **Traefik** et **un conteneur par service** (équivalent « un serveur » en démo).

> **Version Django** : le code utilise **Django 4.2 LTS** (recommandé). Django 2.x est en fin de vie et non compatible avec des versions récentes de Python ; pour un rendu académique, indiquez que la stack est alignée sur les exigences fonctionnelles (REST, JWT, etc.) avec une version maintenue.

## Services

| Service | Rôle |
|--------|------|
| **traefik** | Reverse proxy / load balancer (routage par `Host`) |
| **consul** | Registre / découverte (`:8500`, UI) |
| **rabbitmq** | File de messages (exchange `marketpharm`, clé `order.created`) |
| **postgres-auth** | Base du service auth |
| **postgres-catalog** | Base du catalogue / commandes |
| **auth-service** | JWT (`/api/token/`, refresh), utilisateurs, rôles `ADMIN` / `PHARMACY` / `PRO` |
| **catalog-api** | CRUD + métier : `/api/products/`, `/api/categories/`, `/api/patients/`, `/api/orders/` |
| **notification-worker** | Consommateur asynchrone (simulation notification commande) |
| **web-ui** | Application web classique (templates Django) consommant l’API avec le jeton en session |

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Linux containers)
- Ajouter dans le fichier hosts du système (`/etc/hosts` sur macOS/Linux, `C:\Windows\System32\drivers\etc\hosts` sur Windows) :

```text
127.0.0.1 web.localhost api.localhost auth.localhost
```

## Démarrage

```bash
cd /chemin/vers/pharm
cp .env.example .env   # sous Windows : copy .env.example .env
docker compose up --build
```

Les ports peuvent être mappés autrement dans `docker-compose.yml` (ex. **8081** au lieu de 80). Adaptez les URLs :

- **Interface web** : `http://localhost:8081` (ou `:80` si vous mappez `80:80`)  
- **Traefik dashboard** : `http://localhost:8082` (si `8082:8080` est défini)  
- **Consul** : `http://localhost:8501` (si `8501:8500`)  
- **RabbitMQ management** : `http://localhost:15673` (si `15673:15672`) (`guest` / `guest` par défaut)

### Si ça ne démarre pas (Windows)

1. **`exec /app/entrypoint.sh: no such file or directory`** : fins de ligne Windows (CRLF) dans `entrypoint.sh`. Les Dockerfiles exécutent `sed` pour corriger ; refaites `docker compose build --no-cache`.
2. **`admin.E403` TEMPLATES** : corrigé dans `config/settings.py` (auth + catalogue) ; en cas d’image ancienne : `docker compose build --no-cache auth-service catalog-api`.
3. **Traefik 404 / routeurs en conflit** : les labels utilisent des noms uniques `pharm-web`, `pharm-api`, `pharm-auth`. Si un autre projet Docker expose les mêmes noms de routeur, arrêtez-le ou changez encore le préfixe.
4. **502 juste après `up`** : attendre quelques secondes que Gunicorn soit prêt, puis rafraîchir.

## Comptes de démonstration

Créés au démarrage du service `auth-service` :

| E-mail | Mot de passe | Rôle |
|--------|----------------|------|
| `pro@demo.local` | `demodemo123` | Professionnel |
| `admin@demo.local` | `adminadmin123` | Admin catalogue (JWT) |

## Importer des médicaments / produits depuis un CSV (ex. Kaggle)

1. Créer les catégories de base : `docker compose exec catalog-api python manage.py seed_demo` (ou en local depuis `services/catalog-api`).
2. Placer ton fichier dans `services/catalog-api/data/imports/` (dossier ignoré par Git pour les gros fichiers).
3. Adapter les **noms de colonnes** à ton export : voir `data/products_import_template.csv`.
4. Lancer (exemple) :

```bash
cd services/catalog-api
python manage.py import_products_csv data/imports/mon_export.csv \
  --encoding utf-8-sig \
  --col-name "Drug Name" \
  --col-price "Price" \
  --col-sku "Product ID" \
  --default-category-slug medicaments \
  --dry-run
```

Retirer `--dry-run` une fois les colonnes validées. Options utiles : `--delimiter ";"`, `--price-in-cents`, `--max-rows 500` pour tester.

Le modèle `Product` accepte des noms jusqu’à **500** caractères, descriptions longues (`summary` en texte), SKU jusqu’à **128** caractères, slug jusqu’à **200** caractères (migration `0008`).

### Jeu Kaggle « Pharmacy Products Pricing Egypt » (fichier intégré → stockage **DZD**)

Le fichier `services/catalog-api/data/imports/drugs_egypt.csv` provient du dataset  
[abdurrahmanmorsi/pharmacy-products-pricing-egypt-egp-and-usd](https://www.kaggle.com/datasets/abdurrahmanmorsi/pharmacy-products-pricing-egypt-egp-and-usd)  
(colonnes `name`, `price_EGP`, etc. — sans colonne catégorie).

- **Catégories** : uniquement celles déjà créées par `seed_demo`.  
  L’import applique d’abord des **mots-clés** (anglais) sur le nom ; pour le reste, une **répartition équilibrée** envoie chaque produit vers la catégorie **la moins remplie** afin de remplir tout le catalogue sans inventer de slug.
- **Prix** : le CSV est en **EGP** ; la commande convertit en **dinars algériens (DZD)** avec `EGP_TO_DZD_RATE` (combien de DZD pour 1 EGP). À ajuster dans `.env` selon le cours du jour (valeur indicative).

Import (après `migrate` et `seed_demo`) :

```bash
cd services/catalog-api
python manage.py import_kaggle_egypt_drugs --dry-run   # puis sans --dry-run
```

**web-ui** : affichage en dinar algérien — `CURRENCY_CODE=DZD`, `CURRENCY_SYMBOL=DA` (défaut du projet).

### Devise (Algérie, Égypte, etc.)

Les montants en base sont des **nombres dans ta monnaie locale** (aucune conversion automatique). Pour l’affichage dans **web-ui**, configure dans `.env` ou `docker-compose` :

| Pays | `CURRENCY_CODE` | `CURRENCY_SYMBOL` (exemples) |
|------|-----------------|-------------------------------|
| Algérie | `DZD` | `DA` ou `DZD` |
| Égypte | `EGP` | `ج.م` ou `E£` ou `EGP` |

Exemple Égypte dans `.env` : `CURRENCY_CODE=EGP` et `CURRENCY_SYMBOL=ج.م`

## API (aperçu)

- Obtenir un jeton : `POST http://auth.localhost:8081/api/token/` (ajuster le port si besoin)  
  Corps JSON : `{"email":"pro@demo.local","password":"demodemo123"}`
- Catalogue : `GET http://api.localhost:8081/api/products/` (header `Authorization: Bearer <access>`)
- Commande : `POST http://api.localhost:8081/api/orders/` avec `{"lines":[{"product_id":1,"quantity":2}]}`

**Important** : `JWT_SIGNING_KEY` doit être **identique** entre `auth-service` et `catalog-api` (déjà le cas via `docker-compose.yml` / `.env`).

## Déploiement multi-serveurs

En production, **chaque microservice** peut tourner sur **une machine (ou VM) distincte** : pousser les images vers un registre, puis sur chaque hôte lancer **un seul** service applicatif avec les variables d’environnement pointant vers l’infra partagée (Consul, RabbitMQ, Postgres, etc. sur d’autres serveurs ou services managés). Traefik reste en frontal (serveur dédié ou cluster) ; le routage peut s’appuyer sur les labels Docker, sur la découverte Consul, ou sur un DNS interne selon votre maquette.

Exemple de répartition type (une instance par ligne) :

| Hôte | Services à exécuter |
|------|---------------------|
| S1 | Traefik |
| S2 | Consul |
| S3 | RabbitMQ |
| S4 | postgres-auth |
| S5 | postgres-catalog |
| S6 | auth-service |
| S7 | catalog-api |
| S8 | notification-worker |
| S9 | web-ui |

Adaptez `DATABASE_URL`, `AMQP_URL`, `CONSUL_HTTP_ADDR`, `AUTH_INTERNAL_URL`, `API_INTERNAL_URL` pour viser les **adresses réseau** des autres machines (pas `localhost` entre hôtes).

## Équilibrage de charge (démo)

Avec plusieurs réplicas du même service derrière Traefik :

```bash
docker compose up --build --scale catalog-api=2
```

Traefik répartit le trafic entre les instances (même jeu de labels).

## Découverte Consul

Exemple après démarrage (port **8501** si le mapping du `docker-compose.yml` est `8501:8500`) :

```bash
curl http://localhost:8501/v1/catalog/services
```

Les services HTTP enregistrent un health check sur `/health/` via `docker/scripts/register_consul.py`.

## Contraintes du cahier des charges (synthèse)

| Exigence | Réalisation dans ce dépôt |
|----------|-------------------------|
| API REST métier (CRUD + endpoints métier) | `catalog-api` : `/api/products/`, `/api/categories/`, `/api/patients/`, `/api/orders/`, etc. (DRF ViewSets) |
| Service d’authentification (tokens, rôles) | `auth-service` : JWT (`/api/token/`, refresh), claims `role` / `email`, utilisateurs `ADMIN` / `PHARMACY` / `PRO` |
| UI consommant l’API + auth | `web-ui` : session + appels à l’auth et au catalogue (`apps/shop/api_client.py`) |
| Communication asynchrone (RabbitMQ) | Exchange `marketpharm`, producteur dans `catalog-api` (`messaging.py`), consommateur `notification-worker` |
| Service registry / discovery (Consul) | Enregistrement au démarrage (`register_consul.py`), UI Consul |
| Reverse proxy / load balancer (Traefik) | Service `traefik` avec routage par `Host` et balance si plusieurs réplicas |
| Multi-serveurs | Possible en déployant une image par hôte (section ci-dessus) ; en local, un conteneur par service simule la séparation |
