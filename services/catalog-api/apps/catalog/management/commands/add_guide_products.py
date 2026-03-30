from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Ajoute les produits spécifiques du guide complet"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Supprimer les produits existants avant d'ajouter")
        parser.add_argument("--force", action="store_true", help="Forcer l'ajout même si les produits existent")

    def handle(self, *args, **options):
        if options["reset"]:
            Product.objects.all().delete()
            self.stdout.write("Tous les produits supprimés.")

        # Catégories du guide
        categories_data = {
            'tests': {
                'name': 'Tests',
                'slug': 'tests',
                'description': 'Tests rapides, antigéniques, autotests, diagnostics'
            },
            'masques': {
                'name': 'Masques',
                'slug': 'masques', 
                'description': 'Protection respiratoire, chirurgicaux, FFP2, FFP3'
            },
            'gants': {
                'name': 'Gants',
                'slug': 'gants',
                'description': 'Gants usage professionnel, nitrile, latex, vinyle'
            },
            'consommables': {
                'name': 'Consommables',
                'slug': 'consommables',
                'description': 'Consommables pharmacie, matériel médical'
            },
            'bebe': {
                'name': 'Bébé',
                'slug': 'bebe',
                'description': 'Puériculture et soins bébé, alimentation, hygiène'
            }
        }

        # Créer les catégories
        categories = {}
        for slug, data in categories_data.items():
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults=data
            )
            categories[slug] = category
            if created:
                self.stdout.write(f"✅ Catégorie créée: {data['name']}")

        # Produits du guide - Phase 3 Shopping
        products_data = [
            # Tests
            {
                'category': 'tests',
                'name': 'Test antigénique COVID-19 — boîte 25',
                'slug': 'test-antigenique-covid-25',
                'sku': 'SKU-TST-COV-25',
                'price': Decimal('35.00'),
                'stock': 500,
                'summary': 'Tests antigéniques rapides pour dépistage COVID-19'
            },
            {
                'category': 'tests',
                'name': 'Autotest unitaire COVID-19',
                'slug': 'autotest-covid-unitaire',
                'sku': 'SKU-AUTO-COV-1',
                'price': Decimal('0.40'),
                'stock': 800,
                'summary': 'Autotest individuel pour dépistage COVID-19'
            },
            {
                'category': 'tests',
                'name': 'Test grossesse précoce',
                'slug': 'test-grossesse-precoce',
                'sku': 'SKU-TST-GROS',
                'price': Decimal('2.99'),
                'stock': 150,
                'summary': 'Test de grossesse précoce fiable'
            },
            {
                'category': 'tests',
                'name': 'Test glycémie sanguine',
                'slug': 'test-glycemie-sanguine',
                'sku': 'SKU-TST-GLY',
                'price': Decimal('8.50'),
                'stock': 200,
                'summary': 'Test de glycémie sanguine à domicile'
            },
            {
                'category': 'tests',
                'name': 'Test urinaire complet',
                'slug': 'test-urinaire-complet',
                'sku': 'SKU-TST-URI',
                'price': Decimal('3.99'),
                'stock': 180,
                'summary': 'Test urinaire complet 10 paramètres'
            },
            {
                'category': 'tests',
                'name': 'Test VIH rapide',
                'slug': 'test-vih-rapide',
                'sku': 'SKU-TST-VIH',
                'price': Decimal('15.99'),
                'stock': 80,
                'summary': 'Test de dépistage VIH rapide et fiable'
            },

            # Masques
            {
                'category': 'masques',
                'name': 'Masques chirurgicaux Type IIR — boîte 50',
                'slug': 'masques-chirurgicaux-iir-50',
                'sku': 'SKU-MSK-IIR-50',
                'price': Decimal('12.50'),
                'stock': 300,
                'summary': 'Masques chirurgicaux Type IIR haute protection'
            },
            {
                'category': 'masques',
                'name': 'Masques FFP2 sans valve — boîte 20',
                'slug': 'masques-ffp2-sans-valve-20',
                'sku': 'SKU-MSK-FFP2-20',
                'price': Decimal('25.00'),
                'stock': 200,
                'summary': 'Masques FFP2 sans valve pour protection maximale'
            },
            {
                'category': 'masques',
                'name': 'Masques FFP2 avec valve — boîte 20',
                'slug': 'masques-ffp2-avec-valve-20',
                'sku': 'SKU-MSK-FFP2V-20',
                'price': Decimal('28.00'),
                'stock': 150,
                'summary': 'Masques FFP2 avec valve pour confort respiratoire'
            },
            {
                'category': 'masques',
                'name': 'Masques enfant — boîte 30',
                'slug': 'masques-enfant-30',
                'sku': 'SKU-MSK-ENF-30',
                'price': Decimal('8.99'),
                'stock': 180,
                'summary': 'Masques de protection pour enfants'
            },
            {
                'category': 'masques',
                'name': 'Masques lavable réutilisable',
                'slug': 'masques-lavable-reutilisable',
                'sku': 'SKU-MSK-LAV',
                'price': Decimal('4.99'),
                'stock': 400,
                'summary': 'Masques lavables et réutilisables écologiques'
            },

            # Gants
            {
                'category': 'gants',
                'name': 'Gants nitrile Taille M — boîte 100',
                'slug': 'gants-nitrile-taille-m',
                'sku': 'SKU-GNT-M',
                'price': Decimal('18.90'),
                'stock': 200,
                'summary': 'Gants en nitrile taille M usage médical'
            },
            {
                'category': 'gants',
                'name': 'Gants nitrile Taille L — boîte 100',
                'slug': 'gants-nitrile-taille-l',
                'sku': 'SKU-GNT-L',
                'price': Decimal('19.90'),
                'stock': 200,
                'summary': 'Gants en nitrile taille L usage médical'
            },
            {
                'category': 'gants',
                'name': 'Gants latex Taille M — boîte 100',
                'slug': 'gants-latex-taille-m',
                'sku': 'SKU-GTX-M',
                'price': Decimal('14.90'),
                'stock': 180,
                'summary': 'Gants en latex taille M usage médical'
            },
            {
                'category': 'gants',
                'name': 'Gants chirurgicaux stériles — boîte 50',
                'slug': 'gants-chirurgicaux-steriles-50',
                'sku': 'SKU-GCS-50',
                'price': Decimal('35.00'),
                'stock': 100,
                'summary': 'Gants chirurgicaux stériles haute qualité'
            },
            {
                'category': 'gants',
                'name': 'Gants examen non stériles — boîte 100',
                'slug': 'gants-examen-non-steriles-100',
                'sku': 'SKU-GEX-100',
                'price': Decimal('8.90'),
                'stock': 300,
                'summary': 'Gants d\'examen non stériles usage courant'
            },

            # Consommables
            {
                'category': 'consommables',
                'name': 'Seringue 5ml — boîte 100',
                'slug': 'seringue-5ml-100',
                'sku': 'SKU-SRG-5-100',
                'price': Decimal('4.99'),
                'stock': 300,
                'summary': 'Seringues 5ml stériles usage médical'
            },
            {
                'category': 'consommables',
                'name': 'Seringue 10ml — boîte 100',
                'slug': 'seringue-10ml-100',
                'sku': 'SKU-SRG-10-100',
                'price': Decimal('5.99'),
                'stock': 280,
                'summary': 'Seringues 10ml stériles usage médical'
            },
            {
                'category': 'consommables',
                'name': 'Seringue nasale pédiatrique',
                'slug': 'seringue-nasale-pediatrique',
                'sku': 'SKU-SRG-NAS',
                'price': Decimal('1.45'),
                'stock': 500,
                'summary': 'Seringue nasale pour soins pédiatriques'
            },
            {
                'category': 'consommables',
                'name': 'Aiguille 21G — boîte 100',
                'slug': 'aiguille-21g-100',
                'sku': 'SKU-AIG-21-100',
                'price': Decimal('3.99'),
                'stock': 400,
                'summary': 'Aiguilles 21G stériles usage médical'
            },
            {
                'category': 'consommables',
                'name': 'Compresses stériles 10x10 — boîte 100',
                'slug': 'compresses-steriles-10x10-100',
                'sku': 'SKU-COM-10-100',
                'price': Decimal('8.99'),
                'stock': 250,
                'summary': 'Compresses stériles 10x10cm usage médical'
            },
            {
                'category': 'consommables',
                'name': 'Alcool 70% 100ml',
                'slug': 'alcool-70-100ml',
                'sku': 'SKU-ALC-70-100',
                'price': Decimal('1.99'),
                'stock': 600,
                'summary': 'Alcool à 70% pour désinfection'
            },
            {
                'category': 'consommables',
                'name': 'Bétadine 30ml',
                'slug': 'betadine-30ml',
                'sku': 'SKU-BET-30',
                'price': Decimal('4.99'),
                'stock': 350,
                'summary': 'Bétadine solution antiseptique 30ml'
            },
            {
                'category': 'consommables',
                'name': 'Gaze stérile 10x10 — paquet 10',
                'slug': 'gaze-sterile-10x10',
                'sku': 'SKU-GAZ-10',
                'price': Decimal('3.99'),
                'stock': 300,
                'summary': 'Gaze stérile 10x10cm paquet de 10'
            },
            {
                'category': 'consommables',
                'name': 'Pansement adhésif assorted',
                'slug': 'pansement-adhesif-assorted',
                'sku': 'SKU-PAN-ASS',
                'price': Decimal('5.99'),
                'stock': 250,
                'summary': 'Pansements adhésifs assortis tailles multiples'
            },

            # Bébé
            {
                'category': 'bebe',
                'name': 'Lait premier âge 0-6 mois — 900g',
                'slug': 'lait-premier-age-0-6-mois',
                'sku': 'SKU-LAIT-0-6',
                'price': Decimal('18.99'),
                'stock': 200,
                'summary': 'Lait en poudre premier âge 0-6 mois'
            },
            {
                'category': 'bebe',
                'name': 'Lait deuxième âge 6-12 mois — 900g',
                'slug': 'lait-deuxieme-age-6-12-mois',
                'sku': 'SKU-LAIT-6-12',
                'price': Decimal('19.99'),
                'stock': 180,
                'summary': 'Lait en poudre deuxième âge 6-12 mois'
            },
            {
                'category': 'bebe',
                'name': 'Lait croissance 12-24 mois — 900g',
                'slug': 'lait-croissance-12-24-mois',
                'sku': 'SKU-LAIT-12-24',
                'price': Decimal('20.99'),
                'stock': 160,
                'summary': 'Lait en poudre croissance 12-24 mois'
            },
            {
                'category': 'bebe',
                'name': 'Couches Taille 1 (2-5kg) — paquet 30',
                'slug': 'couches-taille-1-2-5kg',
                'sku': 'SKU-COU-1',
                'price': Decimal('12.99'),
                'stock': 150,
                'summary': 'Couches pour bébé taille 1 (2-5kg)'
            },
            {
                'category': 'bebe',
                'name': 'Couches Taille 2 (4-8kg) — paquet 28',
                'slug': 'couches-taille-2-4-8kg',
                'sku': 'SKU-COU-2',
                'price': Decimal('13.99'),
                'stock': 150,
                'summary': 'Couches pour bébé taille 2 (4-8kg)'
            },
            {
                'category': 'bebe',
                'name': 'Couches Taille 3 (6-10kg) — paquet 26',
                'slug': 'couches-taille-3-6-10kg',
                'sku': 'SKU-COU-3',
                'price': Decimal('14.99'),
                'stock': 140,
                'summary': 'Couches pour bébé taille 3 (6-10kg)'
            },
            {
                'category': 'bebe',
                'name': 'Couches Taille 4 (9-14kg) — paquet 24',
                'slug': 'couches-taille-4-9-14kg',
                'sku': 'SKU-COU-4',
                'price': Decimal('15.99'),
                'stock': 130,
                'summary': 'Couches pour bébé taille 4 (9-14kg)'
            },
            {
                'category': 'bebe',
                'name': 'Biberon anti-colique 250ml',
                'slug': 'biberon-anti-colique-250ml',
                'sku': 'SKU-BIB-250',
                'price': Decimal('8.99'),
                'stock': 200,
                'summary': 'Biberon anti-colique 250ml avec tétine'
            },
            {
                'category': 'bebe',
                'name': 'Biberon 150ml — lot de 3',
                'slug': 'biberon-150ml-lot-3',
                'sku': 'SKU-BIB-150-3',
                'price': Decimal('15.99'),
                'stock': 100,
                'summary': 'Lot de 3 biberons 150ml pour bébé'
            },
            {
                'category': 'bebe',
                'name': 'Gel lavant bébé 500ml',
                'slug': 'gel-lavant-bebe-500ml',
                'sku': 'SKU-GLV-500',
                'price': Decimal('6.99'),
                'stock': 250,
                'summary': 'Gel lavant doux pour bébé 500ml'
            },
            {
                'category': 'bebe',
                'name': 'Crème change bébé 100ml',
                'slug': 'creme-change-bebe-100ml',
                'sku': 'SKU-CRM-100',
                'price': Decimal('4.99'),
                'stock': 300,
                'summary': 'Crème pour change bébé 100ml'
            },
            {
                'category': 'bebe',
                'name': 'Lingettes bébé — paquet 80',
                'slug': 'lingettes-bebe-80',
                'sku': 'SKU-LIN-80',
                'price': Decimal('3.99'),
                'stock': 400,
                'summary': 'Lingettes hygiéniques pour bébé paquet de 80'
            },
            {
                'category': 'bebe',
                'name': 'Thermomètre bébé',
                'slug': 'thermometre-bebe',
                'sku': 'SKU-THM-BB',
                'price': Decimal('12.99'),
                'stock': 150,
                'summary': 'Thermomètre numérique pour bébé'
            },
            {
                'category': 'bebe',
                'name': 'Aspirateur nasal bébé',
                'slug': 'aspirateur-nasal-bebe',
                'sku': 'SKU-ASP-NAS',
                'price': Decimal('8.99'),
                'stock': 180,
                'summary': 'Aspirateur nasal pour bébé'
            },
            {
                'category': 'bebe',
                'name': 'Pack hygiène bébé complet',
                'slug': 'pack-hygiene-bebe-complet',
                'sku': 'SKU-PACK-HYG',
                'price': Decimal('24.00'),
                'stock': 100,
                'summary': 'Pack complet hygiène pour bébé'
            }
        ]

        # Ajouter les produits
        created_count = 0
        updated_count = 0

        for product_data in products_data:
            category = categories[product_data['category']]
            
            if not options["force"] and Product.objects.filter(slug=product_data['slug']).exists():
                self.stdout.write(f"⏭️  {product_data['name']} existe déjà")
                continue

            product, created = Product.objects.update_or_create(
                slug=product_data['slug'],
                defaults={
                    'name': product_data['name'],
                    'category': category,
                    'summary': product_data['summary'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'sku': product_data['sku'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✅ Créé: {product_data['name']} ({product_data['category']})")
            else:
                updated_count += 1
                self.stdout.write(f"🔄 Mis à jour: {product_data['name']} ({product_data['category']})")

        # Statistiques
        total_products = Product.objects.count()
        self.stdout.write(f"\n📊 Statistiques finales:")
        self.stdout.write(f"   Total produits: {total_products}")
        self.stdout.write(f"   Créés: {created_count}")
        self.stdout.write(f"   Mis à jour: {updated_count}")

        # Par catégorie
        self.stdout.write(f"\n📈 Produits par catégorie:")
        for slug, category in categories.items():
            count = Product.objects.filter(category=category).count()
            self.stdout.write(f"   {category.name}: {count} produits")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Produits du guide ajoutés avec succès!"))
