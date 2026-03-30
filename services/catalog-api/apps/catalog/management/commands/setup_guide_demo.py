from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.catalog.models import Product, ProductRating, ProductLike, ProductRecommendation


class Command(BaseCommand):
    help = "Setup complet du guide: produits + ratings + likes + recommandations"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Tout réinitialiser avant setup")

    def handle(self, *args, **options):
        if options["reset"]:
            # Supprimer toutes les données de démo
            ProductRating.objects.all().delete()
            ProductLike.objects.all().delete()
            ProductRecommendation.objects.all().delete()
            self.stdout.write("🗑️  Données de démo supprimées")

        # Créer utilisateurs de démo
        demo_users = []
        for i in range(1, 11):
            user, created = User.objects.get_or_create(
                id=i,
                defaults={
                    'username': f'demo_user_{i}',
                    'email': f'demo_user_{i}@example.com',
                    'first_name': f'Demo User {i}',
                    'password': 'demo123456'
                }
            )
            demo_users.append(user)
            if created:
                self.stdout.write(f"👤 Utilisateur créé: {user.username}")

        # Récupérer les produits
        products = Product.objects.all()
        if not products:
            self.stdout.write("❌ Aucun produit trouvé. Lancez 'add_guide_products' d'abord!")
            return

        self.stdout.write(f"📦 {products.count()} produits trouvés")

        # Ajouter les likes selon le guide
        likes_data = [
            # User 1 likes
            (demo_users[0], products[0]),  # Test COVID
            (demo_users[0], products[6]),  # Masques FFP2
            (demo_users[0], products[11]), # Gants nitrile
            # User 2 likes
            (demo_users[1], products[0]),  # Test COVID
            (demo_users[1], products[7]),  # Masques FFP2 valve
            (demo_users[1], products[12]), # Gants latex
            # User 3 likes
            (demo_users[2], products[1]),  # Autotest
            (demo_users[2], products[8]),  # Masques enfant
            (demo_users[2], products[13]), # Gants chirurgicaux
            # User 4 likes
            (demo_users[3], products[2]),  # Test grossesse
            (demo_users[3], products[9]),  # Masques lavable
            (demo_users[3], products[14]), # Gants examen
            # User 5 likes
            (demo_users[4], products[3]),  # Test glycémie
            (demo_users[4], products[10]), # Masques chirurgicaux
            (demo_users[4], products[15]), # Seringue 5ml
        ]

        likes_count = 0
        for user, product in likes_data:
            like, created = ProductLike.objects.get_or_create(
                user=user,
                product=product
            )
            if created:
                likes_count += 1
                product.user_likes = ProductLike.objects.filter(product=product).count()
                product.save()

        self.stdout.write(f"❤️  {likes_count} likes ajoutés")

        # Ajouter les ratings selon le guide
        ratings_data = [
            # User 1 ratings
            (demo_users[0], products[0], 5, "Excellent test COVID, très fiable!"),
            (demo_users[0], products[6], 4, "Bon masque FFP2, un peu cher"),
            (demo_users[0], products[21], 5, "Lait bébé parfait pour mon nourrisson"),
            # User 2 ratings
            (demo_users[1], products[1], 4, "Autotest pratique et rapide"),
            (demo_users[1], products[7], 5, "Masque FFP2 valve très confortable"),
            (demo_users[1], products[22], 4, "Couches de bonne qualité"),
            # User 3 ratings
            (demo_users[2], products[2], 5, "Test grossesse très précis"),
            (demo_users[2], products[8], 4, "Masques enfant bien adaptés"),
            (demo_users[2], products[23], 5, "Biberons anti-colique efficaces"),
            # User 4 ratings
            (demo_users[3], products[3], 3, "Test glycémie correct mais cher"),
            (demo_users[3], products[9], 4, "Masques lavables écologiques"),
            (demo_users[3], products[24], 3, "Gel lavant correct"),
            # User 5 ratings
            (demo_users[4], products[4], 5, "Test urinaire complet très utile"),
            (demo_users[4], products[10], 5, "Masques chirurgicaux excellents"),
            (demo_users[4], products[25], 4, "Crème change efficace"),
            # User 6 ratings
            (demo_users[5], products[5], 4, "Test VIH fiable et discret"),
            (demo_users[5], products[11], 4, "Gants nitrile de bonne qualité"),
            (demo_users[5], products[26], 5, "Lingettes bébé excellentes"),
            # User 7 ratings
            (demo_users[6], products[12], 3, "Gants latex OK mais allergique"),
            (demo_users[6], products[15], 4, "Seringues de bonne qualité"),
            (demo_users[6], products[27], 4, "Thermomètre bébé précis"),
            # User 8 ratings
            (demo_users[7], products[13], 5, "Gants chirurgicaux parfaits"),
            (demo_users[7], products[16], 4, "Seringues 10ml pratiques"),
            (demo_users[7], products[28], 3, "Aspirateur nasal moyen"),
            # User 9 ratings
            (demo_users[8], products[14], 4, "Gants examen bons rapport qualité/prix"),
            (demo_users[8], products[17], 5, "Seringue nasale indispensable"),
            (demo_users[8], products[29], 5, "Pack hygiène bébé complet"),
            # User 10 ratings
            (demo_users[9], products[18], 4, "Aiguilles de bonne qualité"),
            (demo_users[9], products[19], 3, "Compresses basiques"),
            (demo_users[9], products[20], 5, "Alcool 70% indispensable"),
        ]

        ratings_count = 0
        for user, product, rating, comment in ratings_data:
            rating_obj, created = ProductRating.objects.get_or_create(
                user=user,
                product=product,
                defaults={'rating': rating, 'comment': comment}
            )
            if created:
                ratings_count += 1
                self.stdout.write(f"⭐ {user.username} note {product.name}: {rating}/5")

        self.stdout.write(f"⭐ {ratings_count} ratings ajoutés")

        # Ajouter les recommandations selon le guide
        recommendations_data = [
            # User 1 recommendations
            (demo_users[0], products[0]),  # Test COVID
            (demo_users[0], products[6]),  # Masques FFP2
            (demo_users[0], products[21]), # Lait bébé
            # User 2 recommendations
            (demo_users[1], products[1]),  # Autotest
            (demo_users[1], products[7]),  # Masques FFP2 valve
            (demo_users[1], products[22]), # Couches
            # User 3 recommendations
            (demo_users[2], products[2]),  # Test grossesse
            (demo_users[2], products[8]),  # Masques enfant
            (demo_users[2], products[23]), # Biberons
            # User 4 recommendations
            (demo_users[3], products[3]),  # Test glycémie
            (demo_users[3], products[9]),  # Masques lavables
            (demo_users[3], products[24]), # Gel lavant
            # User 5 recommendations
            (demo_users[4], products[4]),  # Test urinaire
            (demo_users[4], products[10]), # Masques chirurgicaux
            (demo_users[4], products[25]), # Crème change
            # User 6 recommendations
            (demo_users[5], products[5]),  # Test VIH
            (demo_users[5], products[11]), # Gants nitrile
            (demo_users[5], products[26]), # Lingettes bébé
            # User 7 recommendations
            (demo_users[6], products[15]), # Seringues
            (demo_users[6], products[27]), # Thermomètre
            (demo_users[6], products[29]), # Pack hygiène
            # User 8 recommendations
            (demo_users[7], products[13]), # Gants chirurgicaux
            (demo_users[7], products[16]), # Seringues 10ml
            (demo_users[7], products[20]), # Alcool
            # User 9 recommendations
            (demo_users[8], products[14]), # Gants examen
            (demo_users[8], products[17]), # Seringue nasale
            (demo_users[8], products[21]), # Lait bébé
            # User 10 recommendations
            (demo_users[9], products[18]), # Aiguilles
            (demo_users[9], products[19]), # Compresses
            (demo_users[9], products[22]), # Couches
        ]

        recommendations_count = 0
        for user, product in recommendations_data:
            rec, created = ProductRecommendation.objects.get_or_create(
                user=user,
                product=product
            )
            if created:
                recommendations_count += 1
                product.user_recommendations = ProductRecommendation.objects.filter(product=product).count()
                product.save()

        self.stdout.write(f"🎯 {recommendations_count} recommandations ajoutées")

        # Mettre à jour les compteurs sur tous les produits
        for product in products:
            product.user_likes = ProductLike.objects.filter(product=product).count()
            product.user_recommendations = ProductRecommendation.objects.filter(product=product).count()
            product.save()

        # Statistiques finales
        self.stdout.write(f"\n📊 Statistiques finales du setup:")
        self.stdout.write(f"   Utilisateurs créés: {len(demo_users)}")
        self.stdout.write(f"   Produits: {Product.objects.count()}")
        self.stdout.write(f"   Likes: {ProductLike.objects.count()}")
        self.stdout.write(f"   Ratings: {ProductRating.objects.count()}")
        self.stdout.write(f"   Recommandations: {ProductRecommendation.objects.count()}")

        # Moyennes des ratings
        avg_ratings = []
        for product in products[:5]:  # Top 5 produits
            avg = product.get_average_rating()
            if avg > 0:
                avg_ratings.append((product.name, avg))

        if avg_ratings:
            self.stdout.write(f"\n⭐ Top 5 produits par note moyenne:")
            for name, avg in sorted(avg_ratings, key=lambda x: x[1], reverse=True):
                self.stdout.write(f"   {name}: {avg:.1f}/5")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Setup du guide complet terminé avec succès!"))
