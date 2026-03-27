from django.core.management.base import BaseCommand
from apps.catalog.models import Product, ProductRating


class Command(BaseCommand):
    help = "Ajoute des évaluations utilisateurs aux produits"

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des évaluations existent déjà.")

    def handle(self, *args, **options):
        if options["if_empty"] and ProductRating.objects.exists():
            self.stdout.write("Des évaluations existent déjà, opération ignorée.")
            return

        # Get products
        products = Product.objects.all()[:6]
        
        if not products:
            self.stdout.write(self.style.WARNING("Aucun produit trouvé."))
            return

        # Create synthetic ratings
        rating_data = [
            (1, 5), (1, 4), (1, 5),  # User 1: 5, 4, 5
            (2, 4), (2, 4), (2, 5),  # User 2: 4, 4, 5
            (3, 5), (3, 5), (3, 5),  # User 3: 5, 5, 5
            (4, 3), (4, 4), (4, 4),  # User 4: 3, 4, 4
            (5, 4), (5, 5), (5, 3),  # User 5: 4, 5, 3
        ]
        
        added = 0
        for i, (user_id, score) in enumerate(rating_data[:len(products)*3]):
            product = products[i % len(products)]
            rating, created = ProductRating.objects.get_or_create(
                product=product,
                auth_user_id=user_id,
                defaults={"score": score}
            )
            if created:
                added += 1
                avg = float(product.get_average_rating())
                self.stdout.write(f"✅ User {user_id} rates {product.name}: {score}⭐ (avg: {avg:.2f})")
        
        self.stdout.write(self.style.SUCCESS(f"\n✨ {added} évaluations ajoutées au catalogue!"))
