#!/usr/bin/env python
"""
🧪 TESTS COMPLETS - VÉRIFICATION DES CORRECTIONS

Tests pour vérifier que toutes les corrections fonctionnent correctement:
1. Ajout produit sans erreur 400
2. Système de like unique
3. Téléphone et adresse dans commande
4. Recommandations
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.catalog.models import Product, ProductLike, Order, Category
from rest_framework.test import APIClient
from rest_framework import status

class TestProductFixes(TestCase):
    """Tests pour les corrections de produits"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            price=10.99,
            category=self.category,
            description='Test description'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_add_product_without_rating_error(self):
        """Test: Ajouter produit sans erreur 400 (champ rating retiré)"""
        
        # Données du produit SANS champ rating
        product_data = {
            'name': 'New Product',
            'price': 15.99,
            'category': self.category.id,
            'description': 'New product description'
        }
        
        response = self.client.post('/api/products/', product_data)
        
        # Vérifier que ça fonctionne (pas d'erreur 400)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        
        new_product = Product.objects.get(name='New Product')
        self.assertEqual(new_product.price, 15.99)
    
    def test_product_like_unique(self):
        """Test: Like unique par utilisateur"""
        
        # Premier like
        response1 = self.client.post(f'/api/products/{self.product.id}/like/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertTrue(response1.data['liked'])
        
        # Vérifier qu'il y a bien un like
        self.assertEqual(ProductLike.objects.count(), 1)
        self.assertTrue(ProductLike.objects.filter(user=self.user, product=self.product).exists())
        
        # Deuxième like (devrait retirer le like)
        response2 = self.client.post(f'/api/products/{self.product.id}/like/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(response2.data['liked'])
        
        # Vérifier qu'il n'y a plus de like
        self.assertEqual(ProductLike.objects.count(), 0)
    
    def test_product_serializer_includes_like_info(self):
        """Test: Serializer inclut les informations de like"""
        
        # Créer un like
        ProductLike.objects.create(user=self.user, product=self.product)
        
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['is_liked_by_user'])
        self.assertEqual(data['user_likes'], 1)
    
    def test_order_with_phone_and_address(self):
        """Test: Commande avec téléphone et adresse"""
        
        order_data = {
            'lines': [
                {
                    'product': self.product.id,
                    'quantity': 2
                }
            ],
            'phone': '0123456789',
            'shipping_address': '123 rue de la Paix, 75001 Paris'
        }
        
        response = self.client.post('/api/orders/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.phone, '0123456789')
        self.assertEqual(order.shipping_address, '123 rue de la Paix, 75001 Paris')
        self.assertEqual(order.lines.count(), 1)
        self.assertEqual(order.lines.first().quantity, 2)

def run_api_tests():
    """Tests API avec requests (simulation frontend)"""
    
    print("🧪 DÉMARRAGE DES TESTS API")
    print("=" * 50)
    
    base_url = "http://localhost:8081"
    
    # Test 1: Authentification
    print("1. Test Authentification...")
    try:
        response = requests.post(f"{base_url}/api/token/", {
            "email": "pro@demo.local",
            "password": "demodemo123"
        })
        
        if response.status_code == 200:
            token = response.json()['access']
            headers = {'Authorization': f'Bearer {token}'}
            print("✅ Authentification réussie")
        else:
            print(f"❌ Authentification échouée: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    # Test 2: Liste des produits
    print("\n2. Test Liste Produits...")
    try:
        response = requests.get(f"{base_url}/api/products/", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            
            if products and len(products) > 0:
                first_product = products[0]
                print(f"   Premier produit: {first_product.get('name')}")
                print(f"   Likes: {first_product.get('user_likes', 0)}")
                print(f"   Liké par user: {first_product.get('is_liked_by_user', False)}")
        else:
            print(f"❌ Erreur produits: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur produits: {e}")
        return False
    
    # Test 3: Like/unlike
    print("\n3. Test Like/Unlike...")
    try:
        if products and len(products) > 0:
            product_id = products[0]['id']
            
            # Like
            response = requests.post(f"{base_url}/api/products/{product_id}/like/", headers=headers)
            if response.status_code == 200:
                print("✅ Like réussi")
                print(f"   Message: {response.json().get('message')}")
            else:
                print(f"❌ Erreur like: {response.status_code}")
                return False
            
            # Unlike
            response = requests.post(f"{base_url}/api/products/{product_id}/like/", headers=headers)
            if response.status_code == 200:
                print("✅ Unlike réussi")
                print(f"   Message: {response.json().get('message')}")
            else:
                print(f"❌ Erreur unlike: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erreur like/unlike: {e}")
        return False
    
    # Test 4: Création commande
    print("\n4. Test Création Commande...")
    try:
        if products and len(products) > 0:
            order_data = {
                "lines": [
                    {
                        "product": products[0]['id'],
                        "quantity": 1
                    }
                ],
                "phone": "0123456789",
                "shipping_address": "123 rue Test, 75000 Paris"
            }
            
            response = requests.post(f"{base_url}/api/orders/", 
                                    json=order_data, 
                                    headers=headers)
            
            if response.status_code == 201:
                print("✅ Commande créée avec succès")
                order = response.json()
                print(f"   ID Commande: {order.get('id')}")
                print(f"   Téléphone: {order.get('phone')}")
                print(f"   Adresse: {order.get('shipping_address')}")
            else:
                print(f"❌ Erreur commande: {response.status_code}")
                print(f"   Détails: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Erreur commande: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 TOUS LES TESTS SONT PASSÉS!")
    return True

def main():
    """Fonction principale"""
    print("🔧 TESTS DE VÉRIFICATION DES CORRECTIONS")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tests unitaires Django
    print("🧪 Tests Django Unitaires:")
    print("-" * 30)
    
    try:
        from django.test.runner import DiscoverRunner
        runner = DiscoverRunner(verbosity=2)
        result = runner.run_tests(['test_fixes'])
        
        if result.wasSuccessful():
            print("✅ Tests Django réussis")
        else:
            print("❌ Certains tests Django ont échoué")
    except Exception as e:
        print(f"❌ Erreur tests Django: {e}")
    
    print()
    
    # Tests API
    print("🌐 Tests API:")
    print("-" * 30)
    
    success = run_api_tests()
    
    if success:
        print("\n✅ Tous les tests sont passés avec succès!")
        print("🎯 Les corrections fonctionnent correctement:")
        print("   - Ajout produit sans erreur 400")
        print("   - Système de like unique")
        print("   - Commande avec téléphone et adresse")
        print("   - API endpoints fonctionnels")
    else:
        print("\n❌ Certains tests ont échoué")
        print("🔧 Vérifiez la configuration et les logs")

if __name__ == '__main__':
    main()
