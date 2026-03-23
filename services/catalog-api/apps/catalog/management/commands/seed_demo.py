from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Charge un jeu de données type MarketPharm (catégories + produits)."

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des produits existent déjà.")

    def handle(self, *args, **options):
        if options["if_empty"] and Product.objects.exists():
            self.stdout.write("Catalogue déjà peuplé, seed ignoré.")
            return

        data = [
            ("Tests", "tests", "Tests rapides, antigéniques, autotests."),
            ("Masques", "masques", "Protection respiratoire."),
            ("Gants", "gants", "Gants usage professionnel."),
            ("Consommables", "consommables", "Consommables pharmacie."),
            ("Bébé", "bebe", "Puériculture et soins bébé."),
            ("Médicaments", "medicaments", "Médicaments générique et marque."),
            ("Rhume / Grippe", "rhume-grippe", "Soins rhume et grippe."),
            ("Allergie", "allergie", "Médicaments anti-allergie."),
            ("Toux / Gorge", "toux-gorge", "Soins toux et gorge."),
            ("Digestion / Estomac", "digestion-estomac", "Traitement digestion."),
            ("Vitamines", "vitamines", "Comprimés et compléments."),
        ]
        cats = {}
        for name, slug, desc in data:
            c, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "description": desc})
            cats[slug] = c

        samples = [
            ("tests", "Test antigénique — boîte 25", "test-antigenique-25", "SKU-TST-25", Decimal("35.00"), 500),
            ("tests", "Autotest unitaire", "autotest-unitaire", "SKU-AUTO-1", Decimal("0.40"), 800),
            ("masques", "Masques chirurgicaux — boîte 50", "masques-chir-50", "SKU-MSK-50", Decimal("12.50"), 300),
            ("gants", "Gants nitrile M — boîte 100", "gants-nitrile-m", "SKU-GNT-M", Decimal("18.90"), 200),
            ("consommables", "Seringue nasale pédiatrique", "seringue-nasale", "SKU-SRG-01", Decimal("1.45"), 120),
            ("bebe", "Pack hygiène bébé", "pack-bebe", "SKU-BB-01", Decimal("24.00"), 60),
            ("medicaments", "Doliprane 500 mg", "doliprane-500", "SKU-DOL-500", Decimal("40.00"), 150),
            ("medicaments", "Doliprane 1000 mg", "doliprane-1000", "SKU-DOL-1000", Decimal("58.00"), 120),
            ("medicaments", "Doliprane 150 mg sachet", "doliprane-150-sachet", "SKU-DOL-150-S", Decimal("10.50"), 90),
            ("medicaments", "Doliprane 300 mg sachet", "doliprane-300-sachet", "SKU-DOL-300-S", Decimal("12.00"), 80),
            ("medicaments", "Paracetamol générique", "paracetamol-generique", "SKU-PARA-01", Decimal("6.00"), 200),
            ("medicaments", "Dafalgan", "dafalgan", "SKU-DAF-01", Decimal("15.00"), 110),
            ("medicaments", "Ibuprofen", "ibuprofen", "SKU-IBU-01", Decimal("12.00"), 130),
            ("medicaments", "Nurofen", "nurofen", "SKU-NUR-01", Decimal("35.00"), 110),
            ("rhume-grippe", "Fervex", "fervex", "SKU-FER-01", Decimal("28.00"), 90),
            ("rhume-grippe", "Dolirhume", "dolirhume", "SKU-DOLI-01", Decimal("33.00"), 80),
            ("allergie", "Cetirizine", "cetirizine", "SKU-CET-01", Decimal("14.00"), 120),
            ("toux-gorge", "Strepsils", "strepsils", "SKU-STR-01", Decimal("18.00"), 100),
            ("digestion-estomac", "Spasfon", "spasfon", "SKU-SPA-01", Decimal("20.00"), 140),
            ("vitamines", "Vitamine C (Cevit)", "vitamine-c-cevit", "SKU-VIT-C", Decimal("8.00"), 150),
        ]
        for cat_slug, title, pslug, sku, price, stock in samples:
            Product.objects.update_or_create(
                slug=pslug,
                defaults={
                    "name": title,
                    "category": cats[cat_slug],
                    "summary": "Produit professionnel — démo.",
                    "price": price,
                    "stock": stock,
                    "sku": sku,
                },
            )
        self.stdout.write(self.style.SUCCESS("Seed catalogue terminé."))
