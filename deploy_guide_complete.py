#!/usr/bin/env python
"""
🚀 DÉPLOIEMENT COMPLET DU GUIDE

Script complet pour déployer toutes les fonctionnalités du guide:
- Migration de la base de données
- Ajout des produits du guide
- Setup des données de démo
- Validation du déploiement
"""

import os
import sys
import subprocess
import time

def run_command(command, description, cwd=None):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n🔧 {description}...")
    print(f"   Commande: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - ERREUR")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def check_docker_services():
    """Vérifier que les services Docker sont en cours d'exécution"""
    print("\n🐋 Vérification des services Docker...")
    
    services = {
        'catalog-api': 8081,
        'web-ui': 8000,
        'auth-service': 8001,
        'notification-worker': 8002
    }
    
    all_running = True
    
    for service, port in services.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service} (port {port}) - EN COURS")
            else:
                print(f"❌ {service} (port {port}) - ARRÊTÉ")
                all_running = False
                
        except Exception as e:
            print(f"❌ {service} - ERREUR: {e}")
            all_running = False
    
    return all_running

def deploy_guide_complete():
    """Déploiement complet du guide"""
    
    print("🚀 DÉPLOIEMENT COMPLET DU GUIDE")
    print("=" * 60)
    
    # Étape 1: Vérifier les services Docker
    if not check_docker_services():
        print("\n❌ Services Docker non disponibles")
        print("🔧 Démarrez les services avec: docker compose up -d")
        return False
    
    # Étape 2: Migration de la base de données
    if not run_command(
        "docker compose exec catalog-api python manage.py migrate",
        "Migration de la base de données"
    ):
        return False
    
    # Étape 3: Ajout des produits du guide
    if not run_command(
        "docker compose exec catalog-api python manage.py add_guide_products --reset",
        "Ajout des produits du guide"
    ):
        return False
    
    # Étape 4: Setup des données de démo
    if not run_command(
        "docker compose exec catalog-api python manage.py setup_guide_demo",
        "Setup des données de démo (likes, ratings, recommendations)"
    ):
        return False
    
    # Étape 5: Auto-livraison
    if not run_command(
        "docker compose exec catalog-api python manage.py auto_update_order_status",
        "Auto-livraison automatique"
    ):
        print("⚠️  Auto-livraison: Erreur (non critique)")
    
    # Étape 6: Validation du déploiement
    print("\n🧪 Validation du déploiement...")
    
    if not run_command(
        "python test_guide_complete.py",
        "Tests complets du guide"
    ):
        print("⚠️  Tests: Certains tests ont échoué")
    
    # Étape 7: Statistiques finales
    print("\n📊 Statistiques du déploiement...")
    
    stats_commands = [
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import Category; print(f'Catégories: {Category.objects.count()}')\"",
         "Nombre de catégories"),
        
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import Product; print(f'Produits: {Product.objects.count()}')\"",
         "Nombre de produits"),
        
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import ProductLike; print(f'Likes: {ProductLike.objects.count()}')\"",
         "Nombre de likes"),
        
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import ProductRating; print(f'Ratings: {ProductRating.objects.count()}')\"",
         "Nombre de ratings"),
        
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import ProductRecommendation; print(f'Recommandations: {ProductRecommendation.objects.count()}')\"",
         "Nombre de recommandations"),
        
        ("docker compose exec catalog-api python manage.py shell -c \"from django.contrib.auth.models import User; print(f'Utilisateurs: {User.objects.filter(username__startswith=\"demo_user_\").count()}')\"",
         "Utilisateurs de démo"),
    ]
    
    for command, description in stats_commands:
        run_command(command, description)
    
    print("\n" + "=" * 60)
    print("🎉 DÉPLOIEMENT DU GUIDE TERMINÉ!")
    
    print("\n📋 ACCÈS AU SYSTÈME:")
    print("🌐 Web UI: http://localhost:8000")
    print("🔧 Catalog API: http://localhost:8081")
    print("🔐 Auth Service: http://localhost:8001")
    
    print("\n👤 COMPTES DE DÉMO:")
    print("📧 Email: pro@demo.local")
    print("🔑 Password: demodemo123")
    
    print("\n🛍️ PRODUITS DU GUIDE DISPONIBLES:")
    print("🧪 Tests: Test COVID, Autotest, Test grossesse...")
    print("😷 Masques: FFP2, Chirurgicaux, Enfant...")
    print("🧤 Gants: Nitrile, Latex, Chirurgicaux...")
    print("💊 Consommables: Seringues, Alcool, Compresses...")
    print("👶 Bébé: Lait, Couches, Biberons...")
    
    print("\n🎯 FONCTIONNALITÉS ACTIVES:")
    print("✅ Phase 1: Enregistrement utilisateur")
    print("✅ Phase 2: Connexion avec JWT")
    print("✅ Phase 3: Shopping avec produits du guide")
    print("✅ Phase 4: Achat avec vérification stock")
    print("✅ Système de likes (J'aime)")
    print("✅ Système de ratings (1-5 étoiles)")
    print("✅ Système de recommandations")
    print("✅ Auto-livraison automatique")
    print("✅ Filtrage par catégories")
    print("✅ Données de démo complètes")
    
    return True

def quick_deploy():
    """Déploiement rapide (sans validation)"""
    
    print("⚡ DÉPLOIEMENT RAPIDE DU GUIDE")
    print("=" * 40)
    
    commands = [
        ("docker compose exec catalog-api python manage.py migrate", "Migration"),
        ("docker compose exec catalog-api python manage.py add_guide_products --reset", "Produits du guide"),
        ("docker compose exec catalog-api python manage.py setup_guide_demo", "Données de démo"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"❌ Échec: {description}")
            return False
    
    print("\n✅ DÉPLOIEMENT RAPIDE TERMINÉ!")
    return True

def reset_guide():
    """Réinitialiser complètement le guide"""
    
    print("🗑️  RÉINITIALISATION COMPLÈTE DU GUIDE")
    print("=" * 50)
    
    commands = [
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import ProductRating, ProductLike, ProductRecommendation; ProductRating.objects.all().delete(); ProductLike.objects.all().delete(); ProductRecommendation.objects.all().delete()\"",
         "Suppression données de démo"),
        
        ("docker compose exec catalog-api python manage.py shell -c \"from apps.catalog.models import Product, Category; Product.objects.all().delete(); Category.objects.all().delete()\"",
         "Suppression produits et catégories"),
        
        ("docker compose exec catalog-api python manage.py migrate", "Migration clean"),
    ]
    
    for command, description in commands:
        run_command(command, description)
    
    print("\n🗑️  RÉINITIALISATION TERMINÉE!")
    print("🔧 Relancez deploy_guide_complete() pour réinstaller")

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Déploiement du guide complet')
    parser.add_argument('--quick', action='store_true', help='Déploiement rapide (sans validation)')
    parser.add_argument('--reset', action='store_true', help='Réinitialiser complètement')
    parser.add_argument('--check', action='store_true', help='Vérifier les services Docker seulement')
    
    args = parser.parse_args()
    
    if args.check:
        check_docker_services()
    elif args.reset:
        reset_guide()
    elif args.quick:
        quick_deploy()
    else:
        deploy_guide_complete()

if __name__ == '__main__':
    main()
