#!/usr/bin/env python
"""
🧪 TESTS FILTRE PAR CATÉGORIE

Tests pour vérifier le fonctionnement du filtrage des produits par catégorie
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from apps.catalog.models import Product, Category
from rest_framework.test import APIClient
from rest_framework import status

class TestCategoryFilter(TestCase):
    """Tests pour le filtrage par catégorie"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des catégories
        self.cat_medicaments = Category.objects.create(name='Médicaments')
        self.cosmetiques = Category.objects.create(name='Cosmétiques')
        self.equipement = Category.objects.create(name='Équipement médical')
        
        # Créer des produits dans différentes catégories
        self.product1 = Product.objects.create(
            name='Paracétamol',
            price=5.99,
            category=self.cat_medicaments,
            description='Antidouleur'
        )
        
        self.product2 = Product.objects.create(
            name='Crème hydratante',
            price=12.99,
            category=self.cosmetiques,
            description='Pour la peau'
        )
        
        self.product3 = Product.objects.create(
            name='Masque chirurgical',
            price=2.99,
            category=self.equipement,
            description='Protection'
        )
        
        self.product4 = Product.objects.create(
            name='Ibuprofène',
            price=7.99,
            category=self.cat_medicaments,
            description='Anti-inflammatoire'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_filter_by_category_id(self):
        """Test: Filtrer les produits par ID de catégorie"""
        
        # Filtrer par catégorie Médicaments
        response = self.client.get(f'/api/products/?category={self.cat_medicaments.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()
        
        # Vérifier qu'on a bien 2 produits dans cette catégorie
        self.assertEqual(len(products), 2)
        
        # Vérifier que ce sont les bons produits
        product_names = [p['name'] for p in products]
        self.assertIn('Paracétamol', product_names)
        self.assertIn('Ibuprofène', product_names)
        self.assertNotIn('Crème hydratante', product_names)
        self.assertNotIn('Masque chirurgical', product_names)
    
    def test_filter_by_category_name(self):
        """Test: Filtrer les produits par nom de catégorie"""
        
        # Filtrer par nom de catégorie
        response = self.client.get('/api/products/?category_name=Cosmétiques')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()
        
        # Vérifier qu'on a bien 1 produit
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], 'Crème hydratante')
    
    def test_no_category_filter(self):
        """Test: Sans filtre, retourner tous les produits"""
        
        response = self.client.get('/api/products/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()
        
        # Vérifier qu'on a bien tous les produits
        self.assertEqual(len(products), 4)
    
    def test_invalid_category(self):
        """Test: Catégorie invalide retourne liste vide"""
        
        response = self.client.get('/api/products/?category=999')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products = response.json()
        
        # Devrait retourner une liste vide
        self.assertEqual(len(products), 0)

def test_category_filter_api():
    """Test du filtre par catégorie via API REST"""
    
    print("🧪 TEST FILTRE PAR CATÉGORIE")
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
        else:
            print("❌ Authentification échouée")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 1: Obtenir les catégories disponibles
    print("1. Test: Obtenir les catégories...")
    try:
        response = requests.get(f"{base_url}/api/categories/", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ {len(categories)} catégories trouvées")
            
            for cat in categories[:3]:  # Afficher les 3 premières
                print(f"   - {cat.get('name')} (ID: {cat.get('id')})")
            
            if categories:
                first_category = categories[0]
                category_id = first_category['id']
                category_name = first_category['name']
            else:
                print("❌ Aucune catégorie trouvée")
                return False
        else:
            print(f"❌ Erreur catégories: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 2: Filtrer par ID de catégorie
    print(f"\n2. Test: Filtrer par catégorie ID {category_id}...")
    try:
        response = requests.get(f"{base_url}/api/products/?category={category_id}", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés dans cette catégorie")
            
            for product in products[:3]:  # Afficher les 3 premiers
                print(f"   - {product.get('name')} ({product.get('price')}€)")
        else:
            print(f"❌ Erreur filtrage: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 3: Filtrer par nom de catégorie
    print(f"\n3. Test: Filtrer par nom de catégorie '{category_name}'...")
    try:
        response = requests.get(f"{base_url}/api/products/?category_name={category_name}", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            
            for product in products[:3]:
                print(f"   - {product.get('name')} ({product.get('price')}€)")
        else:
            print(f"❌ Erreur filtrage par nom: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Test 4: Vérifier que tous les produits sont dans la bonne catégorie
    print(f"\n4. Test: Vérification des catégories...")
    try:
        response = requests.get(f"{base_url}/api/products/?category={category_id}", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            
            all_correct = True
            for product in products:
                if product.get('category_name') != category_name:
                    print(f"❌ Produit {product.get('name')} dans mauvaise catégorie")
                    all_correct = False
            
            if all_correct:
                print("✅ Tous les produits sont dans la bonne catégorie")
            else:
                return False
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 TESTS FILTRE CATÉGORIE RÉUSSIS!")
    return True

if __name__ == '__main__':
    test_category_filter_api()
