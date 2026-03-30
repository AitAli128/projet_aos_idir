import random
from django.core.management.base import BaseCommand
from apps.catalog.models import Product

class Command(BaseCommand):
    help = "Ajoute images et stock aux produits"

    def add_arguments(self, parser):
        parser.add_argument('--pharmacy-id', type=int, required=True)

    def handle(self, *args, **options):
        pharmacy_id = options['pharmacy_id']
        products = list(Product.objects.all())
        if not products:
            self.stdout.write("Aucun produit trouve.")
            return

        images_par_categorie = {
            "bebe":           "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=400&q=80",
            "tests":          "https://images.unsplash.com/photo-1581093458791-9d42e3c57ac5?w=400&q=80",
            "masques":        "https://images.unsplash.com/photo-1584118624012-df056829fbd0?w=400&q=80",
            "gants":          "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400&q=80",
            "consommables":   "https://images.unsplash.com/photo-1584308666744-24d5e4a8b7dd?w=400&q=80",
            "protection":     "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400&q=80",
            "medicaments":    "https://images.unsplash.com/photo-1550572017-edd951aa8ca6?w=400&q=80",
            "rhume":          "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&q=80",
            "digestion":      "https://images.unsplash.com/photo-1550572017-edd951aa8ca6?w=400&q=80",
            "allergie":       "https://images.unsplash.com/photo-1550572017-edd951aa8ca6?w=400&q=80",
            "premiers-secours":"https://images.unsplash.com/photo-1603398938378-e54eab446dde?w=400&q=80",
            "vitamines":      "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400&q=80",
            "para-pharmacie": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&q=80",
        }

        for p in products:
            p.stock = random.randint(10, 150)
            p.auth_user_id = pharmacy_id
            cat_slug = p.category.slug if p.category else None
            p.image_url = images_par_categorie.get(cat_slug, "https://images.unsplash.com/photo-1550572017-edd951aa8ca6?w=400&q=80")

        Product.objects.bulk_update(products, ['stock', 'image_url', 'auth_user_id'], batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"OK: {len(products)} produits mis a jour!"))
