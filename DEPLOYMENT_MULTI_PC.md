# Guide de Deployment Multi-PC

## Ce qu'il fallait corriger

- `Traefik` sur un seul PC ne peut pas detecter automatiquement des conteneurs Docker qui tournent sur d'autres PCs avec `providers.docker=true`.
- Les fichiers multi-PC pointaient vers `Consul` sur `8500`, alors que le port expose par le PC infrastructure est `8501`.
- Les services distants s'enregistraient dans `Consul` sans IP reseau exploitable depuis les autres PCs. Il faut definir `SERVICE_ADDRESS` avec l'IP reelle du PC.

## Architecture recommandee

- PC 1: infrastructure partagee avec `PostgreSQL`, `RabbitMQ` et `Consul`
- PC 2: `auth-service`
- PC 3: `catalog-api`
- PC 4: `web-ui`

Le `web-ui` appelle `auth-service` et `catalog-api` via `Consul` en priorite. Si `Consul` ne repond pas, il garde des URLs de secours.

## Point important

Tu n'as pas besoin d'un seul gros `docker-compose.yml` pour tous les PCs.
Tu as besoin:
- d'un fichier d'infrastructure
- d'un fichier compose par role de PC
- d'un `.env` par PC

Tu ne peux pas avoir une seule ligne IP pour tout le monde dans tous les cas.
Le minimum realiste est:
- `INFRA_IP` sur tous les PCs
- `SERVICE_ADDRESS` sur chaque PC qui heberge un service

## Ports a ouvrir

- `5432` pour `postgres-auth`
- `5433` pour `postgres-catalog`
- `5673` et `15673` pour `rabbitmq`
- `8501` pour `consul`
- `8000` sur chaque PC qui heberge `auth-service`, `catalog-api` ou `web-ui`

## Etape 1: PC infrastructure

Fichiers:
- `docker-compose.infra.yml`

Commande:

```bash
docker compose -f docker-compose.infra.yml up -d
```

Verification:
- `http://PC_INFRA_IP:8501/ui`
- `http://PC_INFRA_IP:15673`

## Etape 2: PC auth-service

Fichiers:
- `docker-compose.auth.yml`
- dossier `services/auth-service`

`.env`:

```env
INFRA_IP=192.168.1.100
POSTGRES_PASSWORD=auth_secure
JWT_SIGNING_KEY=my-super-secret-key
DJANGO_SECRET_KEY=auth_secret_key
SERVICE_ADDRESS=192.168.1.101
```

Commande:

```bash
docker compose -f docker-compose.auth.yml up -d
```

## Etape 3: PC catalog-api

Fichiers:
- `docker-compose.catalog.yml`
- dossier `services/catalog-api`

`.env`:

```env
INFRA_IP=192.168.1.100
POSTGRES_PASSWORD=catalog_secure
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=rabbitmq_secure
JWT_SIGNING_KEY=my-super-secret-key
DJANGO_SECRET_KEY_CATALOG=catalog_secret_key
SERVICE_ADDRESS=192.168.1.102
```

Commande:

```bash
docker compose -f docker-compose.catalog.yml up -d
```

## Etape 4: PC web-ui

Fichiers:
- `docker-compose.web.yml`
- dossier `services/web-ui`

`.env`:

```env
INFRA_IP=192.168.1.100
AUTH_FALLBACK_IP=192.168.1.101
CATALOG_FALLBACK_IP=192.168.1.102
DJANGO_SECRET_KEY_WEB=web_secret_key
SERVICE_ADDRESS=192.168.1.103
```

Commande:

```bash
docker compose -f docker-compose.web.yml up -d
```

## Acces

Le site doit etre ouvert sur l'IP du PC qui heberge `web-ui`:

```text
http://192.168.1.103:8000
```

Dans `Consul`, tu dois voir:
- `auth-service`
- `catalog-api`
- `web-ui`

## Si un service s'arrete

Si tu coupes `catalog-api` sur son PC:
- `Consul` va le marquer `critical` puis le sortir des instances saines
- le site ne pourra plus charger le catalogue ou les commandes
- c'est normal si tu n'as qu'une seule instance de `catalog-api`

Si tu veux que le site continue de marcher meme quand un PC tombe, il faut au moins 2 instances du meme service sur 2 PCs differents.

## Tests rapides

Depuis le PC web:

```bash
curl http://192.168.1.101:8000/health/
curl http://192.168.1.102:8000/health/
curl http://192.168.1.100:8501/v1/health/service/auth-service?passing=true
curl http://192.168.1.100:8501/v1/health/service/catalog-api?passing=true
```

## Depannage

Si le site ne voit pas un service:
- verifier `SERVICE_ADDRESS`
- verifier le pare-feu Windows
- verifier que `CONSUL_HTTP_ADDR` pointe vers `http://INFRA_IP:8501`
- verifier dans `Consul` que le service est `passing`

Si la base ne repond pas:
- verifier que le PC infrastructure est allume
- verifier `POSTGRES_PASSWORD`
- verifier que le port `5432` ou `5433` est ouvert

## Commandes utiles

```bash
docker compose -f docker-compose.auth.yml logs -f
docker compose -f docker-compose.catalog.yml logs -f
docker compose -f docker-compose.web.yml logs -f
docker compose -f docker-compose.infra.yml logs -f consul
```
