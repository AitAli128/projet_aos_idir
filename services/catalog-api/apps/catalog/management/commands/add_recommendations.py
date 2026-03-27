from django.core.management.base import BaseCommand
from apps.catalog.models import Product, ProductRecommendation


class Command(BaseCommand):
    help = "Ajoute des recommandations utilisateur aux produits existants"

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des recommandations existent déjà.")

    def handle(self, *args, **options):
        if options["if_empty"] and ProductRecommendation.objects.exists():
            self.stdout.write("Des recommandations existent déjà, opération ignorée.")
            return

        # Get the first few products
        products = Product.objects.all()[:4]
        
        if not products:
            self.stdout.write(self.style.WARNING("Aucun produit trouvé. Seed vide ?"))
            return

        # Add recommendations from different synthetic users
        user_ids = [1, 2, 3, 4, 5, 6]
        
        for product in products:
            for user_id in user_ids[:3]:  # 3 users per product
                ProductRecommendation.objects.get_or_create(
                    product=product,
                    auth_user_id=user_id
                )
                product.user_recommendations += 1
            
            product.save()

        self.stdout.write(self.style.SUCCESS("✅ Recommandations utilisateur ajoutées avec succès."))
