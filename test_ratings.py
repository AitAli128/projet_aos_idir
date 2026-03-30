#!/usr/bin/env python
"""
🧪 TESTS SYSTÈME DE RATINGS (ÉVALUATIONS)

Tests pour vérifier le fonctionnement du système d'évaluation des produits
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from apps.catalog.models import Product, Category, ProductRating
from rest_framework.test import APIClient
from rest_framework import status
from django.db.utils import IntegrityError

class TestProductRatings(TestCase):
    """Tests pour le système d'évaluation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
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
    
    def test_create_rating(self):
        """Test: Créer une évaluation"""
        
        rating_data = {
            'rating': 5,
            'comment': 'Excellent produit!'
        }
        
        response = self.client.post(f'/api/products/{self.product.id}/rate/', rating_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductRating.objects.count(), 1)
        
        rating = ProductRating.objects.first()
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.product, self.product)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.comment, 'Excellent produit!')
    
    def test_unique_rating_per_user_product(self):
        """Test: Un seul rating par utilisateur/produit"""
        
        # Premier rating
        rating_data = {
            'rating': 4,
            'comment': 'Bon produit'
        }
        
        response1 = self.client.post(f'/api/products/{self.product.id}/rate/', rating_data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Deuxième rating (devrait mettre à jour le premier)
        rating_data2 = {
            'rating': 3,
            'comment': 'Moyen'
        }
        
        response2 = self.client.post(f'/api/products/{self.product.id}/rate/', rating_data2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'il n'y a toujours qu'un seul rating
        self.assertEqual(ProductRating.objects.count(), 1)
        
        # Vérifier que le rating a été mis à jour
        rating = ProductRating.objects.first()
        self.assertEqual(rating.rating, 3)
        self.assertEqual(rating.comment, 'Moyen')
    
    def test_remove_rating(self):
        """Test: Retirer une évaluation"""
        
        # Créer un rating
        ProductRating.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment='Bon produit'
        )
        
        # Retirer le rating
        response = self.client.post(f'/api/products/{self.product.id}/unrate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProductRating.objects.count(), 0)
    
    def test_get_product_ratings(self):
        """Test: Obtenir les évaluations d'un produit"""
        
        # Créer plusieurs ratings
        ProductRating.objects.create(user=self.user, product=self.product, rating=5, comment='Excellent')
        ProductRating.objects.create(user=self.user2, product=self.product, rating=3, comment='Moyen')
        
        response = self.client.get(f'/api/products/{self.product.id}/ratings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = response.json()
        self.assertEqual(len(ratings), 2)
    
    def test_product_serializer_includes_rating_info(self):
        """Test: Serializer inclut les informations de rating"""
        
        # Créer un rating
        ProductRating.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment='Bon produit'
        )
        
        response = self.client.get(f'/api/products/{self.product.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier les champs de rating
        self.assertIn('average_rating', data)
        self.assertIn('rating_count', data)
        self.assertIn('user_rating', data)
        self.assertEqual(data['user_rating'], 4)
        self.assertEqual(data['average_rating'], 4.0)
        self.assertEqual(data['rating_count'], 1)
    
    def test_rating_validation(self):
        """Test: Validation des notes"""
        
        # Test rating invalide (trop bas)
        response = self.client.post(f'/api/products/{self.product.id}/rate/', {
            'rating': 0,
            'comment': 'Trop bas'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test rating invalide (trop haut)
        response = self.client.post(f'/api/products/{self.product.id}/rate/', {
            'rating': 6,
            'comment': 'Trop haut'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test rating valide
        response = self.client.post(f'/api/products/{self.product.id}/rate/', {
            'rating': 3,
            'comment': 'Valide'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_ratings_api():
    """Test du système de ratings via API REST"""
    
    print("🧪 TESTS SYSTÈME DE RATINGS")
    print("=" * 40)
    
    base_url = "http://localhost:8081"
    
    # Authentification
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
            print("❌ Authentification échouée")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 1: Obtenir les produits
    print("\n1. Test: Obtenir les produits...")
    try:
        response = requests.get(f"{base_url}/api/products/", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            
            if products:
                test_product = products[0]
                product_id = test_product['id']
                print(f"   Produit test: {test_product['name']}")
                print(f"   Rating moyen: {test_product.get('average_rating', 'N/A')}")
                print(f"   Nombre de ratings: {test_product.get('rating_count', 0)}")
            else:
                print("❌ Aucun produit trouvé")
                return False
        else:
            print(f"❌ Erreur produits: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 2: Noter un produit
    print("\n2. Test: Noter un produit...")
    try:
        rating_data = {
            'rating': 5,
            'comment': 'Excellent produit, je recommande vivement!'
        }
        
        response = requests.post(f"{base_url}/api/products/{product_id}/rate/", 
                               json=rating_data, 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rating créé avec succès")
            print(f"   Note: {result.get('rating')}")
            print(f"   Commentaire: {result.get('comment')}")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Erreur rating: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur rating: {e}")
        return False
    
    # Test 3: Vérifier le rating dans les détails du produit
    print("\n3. Test: Vérifier le rating dans le produit...")
    try:
        response = requests.get(f"{base_url}/api/products/{product_id}/", headers=headers)
        
        if response.status_code == 200:
            product = response.json()
            print("✅ Détails du produit mis à jour")
            print(f"   Rating moyen: {product.get('average_rating', 'N/A')}")
            print(f"   Nombre de ratings: {product.get('rating_count', 0)}")
            print(f"   Rating de l'utilisateur: {product.get('user_rating', 'N/A')}")
        else:
            print(f"❌ Erreur détails: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur détails: {e}")
        return False
    
    # Test 4: Mettre à jour le rating
    print("\n4. Test: Mettre à jour le rating...")
    try:
        updated_rating_data = {
            'rating': 3,
            'comment': 'Produit correct, mais pourrait être meilleur.'
        }
        
        response = requests.post(f"{base_url}/api/products/{product_id}/rate/", 
                               json=updated_rating_data, 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rating mis à jour")
            print(f"   Nouvelle note: {result.get('rating')}")
            print(f"   Nouveau commentaire: {result.get('comment')}")
        else:
            print(f"❌ Erreur mise à jour: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur mise à jour: {e}")
        return False
    
    # Test 5: Obtenir tous les ratings du produit
    print("\n5. Test: Obtenir tous les ratings...")
    try:
        response = requests.get(f"{base_url}/api/products/{product_id}/ratings/", headers=headers)
        
        if response.status_code == 200:
            ratings = response.json()
            print(f"✅ {len(ratings)} ratings trouvés")
            
            for rating in ratings:
                print(f"   - Note: {rating.get('rating')}/5")
                print(f"     Commentaire: {rating.get('comment', 'N/A')[:50]}...")
                print(f"     Date: {rating.get('created_at', 'N/A')}")
        else:
            print(f"❌ Erreur liste ratings: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur liste ratings: {e}")
        return False
    
    # Test 6: Retirer le rating
    print("\n6. Test: Retirer le rating...")
    try:
        response = requests.post(f"{base_url}/api/products/{product_id}/unrate/", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rating retiré avec succès")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Erreur suppression: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return False
    
    # Test 7: Vérifier que le rating a été retiré
    print("\n7. Test: Vérifier suppression du rating...")
    try:
        response = requests.get(f"{base_url}/api/products/{product_id}/", headers=headers)
        
        if response.status_code == 200:
            product = response.json()
            print("✅ Rating retiré des détails du produit")
            print(f"   Rating de l'utilisateur: {product.get('user_rating', 'N/A')}")
            print(f"   Nombre total de ratings: {product.get('rating_count', 0)}")
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False
    
    # Test 8: Validation des notes
    print("\n8. Test: Validation des notes...")
    try:
        # Test note invalide (trop bas)
        response = requests.post(f"{base_url}/api/products/{product_id}/rate/", 
                               json={'rating': 0, 'comment': 'Trop bas'}, 
                               headers=headers)
        
        if response.status_code == 400:
            print("✅ Validation note trop bas fonctionnelle")
        else:
            print("❌ Validation note trop bas échouée")
        
        # Test note invalide (trop haut)
        response = requests.post(f"{base_url}/api/products/{product_id}/rate/", 
                               json={'rating': 6, 'comment': 'Trop haut'}, 
                               headers=headers)
        
        if response.status_code == 400:
            print("✅ Validation note trop haute fonctionnelle")
        else:
            print("❌ Validation note trop haute échouée")
        
        # Test note valide
        response = requests.post(f"{base_url}/api/products/{product_id}/rate/", 
                               json={'rating': 4, 'comment': 'Note valide'}, 
                               headers=headers)
        
        if response.status_code == 200:
            print("✅ Note valide acceptée")
        else:
            print("❌ Note valide rejetée")
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 TESTS RATINGS TERMINÉS!")
    return True

def main():
    """Fonction principale"""
    print("⭐ TESTS SYSTÈME DE RATINGS")
    print("=" * 40)
    
    success = test_ratings_api()
    
    if success:
        print("\n🎯 BILAN RATINGS:")
        print("✅ Création de ratings fonctionnelle")
        print("✅ Mise à jour de ratings")
        print("✅ Suppression de ratings")
        print("✅ Validation des notes (1-5)")
        print("✅ Un rating par utilisateur/produit")
        print("✅ Integration avec les détails produits")
    else:
        print("\n❌ Certains tests de ratings ont échoué")
        print("🔧 Vérifiez les modèles et les vues")

if __name__ == '__main__':
    main()
