from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Ajoute des produits supplémentaires au catalogue"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force l'ajout même si les produits existent")

    def handle(self, *args, **options):
        # Additional products to add
        new_products = [
            {
                "cat_slug": "tests",
                "title": "Test PCR — kit 5 tests",
                "slug": "test-pcr-5",
                "sku": "SKU-PCR-5",
                "price": Decimal("75.00"),
                "stock": 150,
            },
            {
                "cat_slug": "tests",
                "title": "Thermomètre infrarouge sans contact",
                "slug": "thermometre-ir",
                "sku": "SKU-THM-IR",
                "price": Decimal("28.50"),
                "stock": 200,
            },
            {
                "cat_slug": "masques",
                "title": "Masques FFP2 — boîte 20",
                "slug": "masques-ffp2-20",
                "sku": "SKU-FFP2-20",
                "price": Decimal("19.90"),
                "stock": 400,
            },
            {
                "cat_slug": "masques",
                "title": "Masques KN95 — boîte 20",
                "slug": "masques-kn95-20",
                "sku": "SKU-KN95-20",
                "price": Decimal("17.50"),
                "stock": 350,
            },
            {
                "cat_slug": "gants",
                "title": "Gants latex S — boîte 100",
                "slug": "gants-latex-s",
                "sku": "SKU-GLT-S",
                "price": Decimal("16.75"),
                "stock": 180,
            },
            {
                "cat_slug": "gants",
                "title": "Gants vitrile non poudrés — boîte 100",
                "slug": "gants-vitrile-100",
                "sku": "SKU-VTR-100",
                "price": Decimal("12.30"),
                "stock": 250,
            },
            {
                "cat_slug": "consommables",
                "title": "Désinfectant surface — 500 ml",
                "slug": "desinfectant-500ml",
                "sku": "SKU-DSF-500",
                "price": Decimal("8.90"),
                "stock": 400,
            },
            {
                "cat_slug": "consommables",
                "title": "Gel hydro-alcoolique — 100 ml",
                "slug": "gel-alcool-100ml",
                "sku": "SKU-GEL-100",
                "price": Decimal("3.50"),
                "stock": 600,
            },
            {
                "cat_slug": "bebe",
                "title": "Lingettes bébé hydratantes — 56 lingettes",
                "slug": "lingettes-bebe-56",
                "sku": "SKU-LNG-56",
                "price": Decimal("4.99"),
                "stock": 500,
            },
            {
                "cat_slug": "bebe",
                "title": "Crème change bébé — 100 ml",
                "slug": "creme-change-100",
                "sku": "SKU-CRM-100",
                "price": Decimal("6.75"),
                "stock": 300,
            },
        ]

        # Get or create categories
        categories = {}
        for cat_slug in set(p["cat_slug"] for p in new_products):
            categories[cat_slug] = Category.objects.filter(slug=cat_slug).first()

        # Add products
        added_count = 0
        for prod_data in new_products:
            cat = categories.get(prod_data["cat_slug"])
            if not cat:
                self.stdout.write(self.style.WARNING(f"Catégorie {prod_data['cat_slug']} non trouvée"))
                continue

            if not options["force"] and Product.objects.filter(slug=prod_data["slug"]).exists():
                self.stdout.write(f"⏭️  {prod_data['title']} exists - skip")
                continue

            Product.objects.update_or_create(
                slug=prod_data["slug"],
                defaults={
                    "name": prod_data["title"],
                    "category": cat,
                    "summary": "Produit professionnel de qualité",
                    "price": prod_data["price"],
                    "stock": prod_data["stock"],
                    "sku": prod_data["sku"],
                },
            )
            added_count += 1
            self.stdout.write(f"✅ {prod_data['title']}")

        self.stdout.write(self.style.SUCCESS(f"\n✨ {added_count} nouveaux produits ajoutés au catalogue!"))
