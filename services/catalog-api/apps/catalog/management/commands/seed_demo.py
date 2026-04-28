from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Charge un jeu de donnees catalogue plus riche pour la demo."

    CATEGORY_IMAGES = {
        "bebe": "/static/shop/img/bebe.png",
        "tests": "/static/shop/img/tests.png",
        "masques": "/static/shop/img/masks.png",
        "gants": "/static/shop/img/gloves.png",
        "consommables": "/static/shop/img/cons.png",
        "protection": "/static/shop/img/gloves.png",
        "medicaments": "/static/shop/img/cons.png",
        "rhume": "/static/shop/img/tests.png",
        "digestion": "/static/shop/img/cons.png",
        "allergie": "/static/shop/img/tests.png",
        "premiers-secours": "/static/shop/img/cons.png",
        "vitamines": "/static/shop/img/bebe.png",
        "para-pharmacie": "/static/shop/img/bebe.png",
    }

    CATEGORY_BRANDS = {
        "bebe": "BabyCare",
        "tests": "DiagnoLab",
        "masques": "SafeAir",
        "gants": "MediGrip",
        "consommables": "ClinicLine",
        "protection": "Protect+",
        "medicaments": "PharmaPlus",
        "rhume": "Respira",
        "digestion": "DigestZen",
        "allergie": "Allergo",
        "premiers-secours": "UrgenceCare",
        "vitamines": "Vitalis",
        "para-pharmacie": "Dermalab",
    }

    FEATURED_SLUGS = {
        "test-covid",
        "masque-ffp2",
        "gants-nitrile",
        "gel-hydro",
        "paracetamol-500",
        "fervex",
        "multivitamines",
        "creme-solaire",
    }

    SPECIAL_STOCK = {
        "test-vih": 0,
        "masque-ffp2": 8,
        "thermometre-infra": 5,
        "gel-acne": 6,
        "gants-nitrile": 9,
    }

    SPECIAL_EXPIRATION_DAYS = {
        "fervex": 20,
        "smecta": 32,
        "paracetamol-500": 120,
        "ibuprofene-400": 90,
        "test-covid": 18,
        "vitamine-c": 65,
    }

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Ne rien faire si des produits existent deja.")
        parser.add_argument("--reset", action="store_true", help="Supprimer les produits existants avant recreation.")

    def handle(self, *args, **options):
        if options["reset"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Catalogue supprime.")

        if options["if_empty"] and Product.objects.exists():
            self.stdout.write("Catalogue deja peuple, seed ignore.")
            return

        category_rows = [
            ("Bebes", "bebe", "Puericulture, hygiene et alimentation infantile."),
            ("Tests medicaux", "tests", "Tests rapides, autotests et outils de depistage."),
            ("Masques", "masques", "Masques chirurgicaux, FFP2 et protection respiratoire."),
            ("Gants", "gants", "Gants medicaux et consommables de protection."),
            ("Consommables", "consommables", "Consommables de soin pour officines et cliniques."),
            ("Gants et protection", "protection", "Equipements de protection pour structures de sante."),
            ("Medicaments", "medicaments", "References de comptoir et produits a rotation forte."),
            ("Rhume et grippe", "rhume", "Produits saisonniers pour les symptomes respiratoires."),
            ("Digestion", "digestion", "Soutien digestif et confort gastrique."),
            ("Allergies", "allergie", "Solutions antiallergiques du quotidien."),
            ("Premiers secours", "premiers-secours", "Urgence, desinfection et soins rapides."),
            ("Vitamines", "vitamines", "Complements nutritionnels et soutien tonique."),
            ("Para-pharmacie", "para-pharmacie", "Soin, hygiene et dermocosmetique."),
        ]

        categories = {}
        for name, slug, description in category_rows:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description},
            )
            categories[slug] = category

        samples = [
            ("bebe", "Lait infantile 1er age", "lait-1er-age", "SKU-BEBE-L1", Decimal("2600.00"), 100),
            ("bebe", "Lait 2eme age", "lait-2eme-age", "SKU-BEBE-L2", Decimal("2800.00"), 100),
            ("bebe", "Lait anti-colique", "lait-anti-colique", "SKU-BEBE-LAC", Decimal("3200.00"), 80),
            ("bebe", "Couches bebe Pampers", "couches-pampers", "SKU-BEBE-COU", Decimal("2200.00"), 150),
            ("bebe", "Lingettes bebe", "lingettes-bebe", "SKU-BEBE-LIN", Decimal("260.00"), 200),
            ("bebe", "Creme erytheme fessier", "creme-erytheme", "SKU-BEBE-CRM", Decimal("420.00"), 120),
            ("bebe", "Serum physiologique", "serum-physio", "SKU-BEBE-SER", Decimal("210.00"), 300),
            ("bebe", "Thermometre digital", "thermometre-digital", "SKU-BEBE-THD", Decimal("1200.00"), 50),
            ("bebe", "Gel lavant bebe", "gel-lavant-bebe", "SKU-BEBE-GEL", Decimal("900.00"), 100),
            ("bebe", "Huile bebe", "huile-bebe", "SKU-BEBE-HUI", Decimal("700.00"), 90),
            ("tests", "Test grossesse", "test-grossesse", "SKU-TST-GRO", Decimal("320.00"), 200),
            ("tests", "Test ovulation", "test-ovulation", "SKU-TST-OVU", Decimal("450.00"), 150),
            ("tests", "Test glycemie appareil", "test-glycemie-app", "SKU-TST-GLY", Decimal("1200.00"), 60),
            ("tests", "Bandelettes glycemie", "bandelettes-glycemie", "SKU-TST-BAN", Decimal("2500.00"), 100),
            ("tests", "Test COVID antigenique", "test-covid", "SKU-TST-COV", Decimal("620.00"), 300),
            ("tests", "Test urinaire", "test-urinaire", "SKU-TST-URI", Decimal("330.00"), 150),
            ("tests", "Test cholesterol", "test-cholesterol", "SKU-TST-CHO", Decimal("1900.00"), 80),
            ("tests", "Test VIH rapide", "test-vih", "SKU-TST-VIH", Decimal("1750.00"), 50),
            ("masques", "Masque chirurgical Type IIR", "masque-iir", "SKU-MSK-IIR", Decimal("0.50"), 1000),
            ("masques", "Masque FFP2 sans valve", "masque-ffp2", "SKU-MSK-FFP2", Decimal("0.80"), 500),
            ("masques", "Masque enfant taille S", "masque-enfant", "SKU-MSK-ENF", Decimal("0.45"), 300),
            ("masques", "Masque lavable reutilisable", "masque-lavable", "SKU-MSK-LAV", Decimal("3.99"), 100),
            ("masques", "Masque KN95", "masque-kn95", "SKU-MSK-KN95", Decimal("0.75"), 400),
            ("gants", "Gants nitrile taille M", "gants-nitrile-m", "SKU-GNT-NIT-M", Decimal("0.15"), 1000),
            ("gants", "Gants latex taille L", "gants-latex-l", "SKU-GNT-LTX-L", Decimal("0.12"), 800),
            ("gants", "Gants vinyle taille S", "gants-vinyle-s", "SKU-GNT-VIN-S", Decimal("0.10"), 600),
            ("gants", "Gants chirurgicaux steriles", "gants-chirurgicaux", "SKU-GNT-CHIR", Decimal("0.25"), 200),
            ("gants", "Gants examen non steriles", "gants-examen", "SKU-GNT-EXAM", Decimal("0.08"), 1200),
            ("consommables", "Seringue 5ml", "seringue-5ml", "SKU-CON-SER5", Decimal("0.20"), 500),
            ("consommables", "Compresses steriles 10x10", "compresses-10x10", "SKU-CON-COMP", Decimal("2.99"), 200),
            ("consommables", "Bande elastique 5cm", "bande-5cm", "SKU-CON-BAND", Decimal("1.99"), 150),
            ("consommables", "Alcool 70% 100ml", "alcool-70-100ml", "SKU-CON-ALC", Decimal("1.49"), 300),
            ("consommables", "Betadine 30ml", "betadine-30ml", "SKU-CON-BET", Decimal("3.99"), 100),
            ("protection", "Gants latex boite 100", "gants-latex", "SKU-PRO-GLX", Decimal("2250.00"), 120),
            ("protection", "Gants nitrile boite 100", "gants-nitrile", "SKU-PRO-GNT", Decimal("2650.00"), 100),
            ("protection", "Masques chirurgicaux boite 50", "masques-chir", "SKU-PRO-MSK", Decimal("550.00"), 200),
            ("protection", "Gel hydroalcoolique 500ml", "gel-hydro", "SKU-PRO-GEL", Decimal("500.00"), 150),
            ("protection", "Thermometre infrarouge", "thermometre-infra", "SKU-PRO-THI", Decimal("6500.00"), 40),
            ("medicaments", "Paracetamol 500mg", "paracetamol-500", "SKU-MED-PAR", Decimal("225.00"), 500),
            ("medicaments", "Ibuprofene 400mg", "ibuprofene-400", "SKU-MED-IBU", Decimal("350.00"), 400),
            ("medicaments", "Aspirine 100mg", "aspirine-100", "SKU-MED-ASP", Decimal("175.00"), 300),
            ("medicaments", "Diclofenac gel 1%", "diclofenac-gel", "SKU-MED-DIC", Decimal("500.00"), 200),
            ("medicaments", "Spasfon", "spasfon", "SKU-MED-SPA", Decimal("450.00"), 250),
            ("rhume", "Fervex Adulte", "fervex", "SKU-RHU-FER", Decimal("475.00"), 300),
            ("rhume", "Humex Rhume", "humex", "SKU-RHU-HUM", Decimal("550.00"), 250),
            ("rhume", "Vitamine C 1000mg", "vitamine-c", "SKU-RHU-VIT", Decimal("300.00"), 400),
            ("rhume", "Spray nasal", "spray-nasal", "SKU-RHU-SPR", Decimal("375.00"), 350),
            ("rhume", "Sirop toux seche et grasse", "sirop-toux", "SKU-RHU-SIR", Decimal("500.00"), 280),
            ("digestion", "Gaviscon Suspension", "gaviscon", "SKU-DIG-GAV", Decimal("650.00"), 200),
            ("digestion", "Maalox Anti-acide", "maalox", "SKU-DIG-MAA", Decimal("550.00"), 220),
            ("digestion", "Smecta 3g", "smecta", "SKU-DIG-SME", Decimal("450.00"), 300),
            ("digestion", "Charbon actif", "charbon-actif", "SKU-DIG-CHA", Decimal("350.00"), 250),
            ("digestion", "Sirop digestif", "sirop-digestif", "SKU-DIG-SIR", Decimal("500.00"), 180),
            ("allergie", "Cetirizine 10mg", "cetirizine", "SKU-ALL-CET", Decimal("300.00"), 200),
            ("allergie", "Loratadine 10mg", "loratadine", "SKU-ALL-LOR", Decimal("350.00"), 180),
            ("allergie", "Creme antihistaminique", "creme-anti-hist", "SKU-ALL-CRM", Decimal("450.00"), 150),
            ("premiers-secours", "Betadine solution dermique", "betadine", "SKU-SEC-BET", Decimal("450.00"), 200),
            ("premiers-secours", "Pansements adhesifs boite", "pansements", "SKU-SEC-PAN", Decimal("225.00"), 300),
            ("premiers-secours", "Alcool medical 70%", "alcool-medical", "SKU-SEC-ALC", Decimal("300.00"), 250),
            ("premiers-secours", "Compresses steriles", "compresses", "SKU-SEC-COM", Decimal("350.00"), 300),
            ("premiers-secours", "Eau oxygenee", "eau-oxygenee", "SKU-SEC-EAU", Decimal("300.00"), 220),
            ("vitamines", "Multivitamines A-Z", "multivitamines", "SKU-VIT-MUL", Decimal("600.00"), 150),
            ("vitamines", "Magnesium B6", "magnesium", "SKU-VIT-MAG", Decimal("500.00"), 200),
            ("vitamines", "Fer + Acide Folique", "fer", "SKU-VIT-FER", Decimal("450.00"), 180),
            ("vitamines", "Omega 3", "omega-3", "SKU-VIT-OME", Decimal("900.00"), 120),
            ("para-pharmacie", "Creme hydratante corps visage", "creme-hydratante", "SKU-PAR-HYD", Decimal("1000.00"), 100),
            ("para-pharmacie", "Creme solaire SPF 50+", "creme-solaire", "SKU-PAR-SOL", Decimal("1650.00"), 80),
            ("para-pharmacie", "Baume a levres", "baume-levres", "SKU-PAR-BAU", Decimal("350.00"), 200),
            ("para-pharmacie", "Shampooing antipelliculaire", "shampooing", "SKU-PAR-SHA", Decimal("1100.00"), 120),
            ("para-pharmacie", "Dentifrice blancheur", "dentifrice", "SKU-PAR-DEN", Decimal("350.00"), 300),
            ("para-pharmacie", "Brosse a dents", "brosse-a-dents", "SKU-PAR-BAD", Decimal("275.00"), 250),
            ("para-pharmacie", "Bain de bouche", "bain-bouche", "SKU-PAR-BAI", Decimal("650.00"), 180),
            ("para-pharmacie", "Gel anti-acne", "gel-acne", "SKU-PAR-ACN", Decimal("1050.00"), 100),
            ("para-pharmacie", "Solution lentilles", "solution-lentilles", "SKU-PAR-SLN", Decimal("1400.00"), 70),
        ]

        created_count = 0
        updated_count = 0

        for category_slug, name, slug, sku, price, stock in samples:
            _, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": categories[category_slug],
                    "brand": self._infer_brand(category_slug, name),
                    "summary": self._build_summary(category_slug, name),
                    "image_url": self.CATEGORY_IMAGES.get(category_slug, "/static/img/logo.png"),
                    "unit_label": self._infer_unit_label(category_slug, name),
                    "price": price,
                    "stock": self.SPECIAL_STOCK.get(slug, stock),
                    "low_stock_threshold": self._infer_low_stock_threshold(category_slug),
                    "min_order_quantity": self._infer_min_order_quantity(category_slug, name),
                    "sku": sku,
                    "expiration_date": self._infer_expiration_date(slug, category_slug),
                    "is_featured": slug in self.FEATURED_SLUGS,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        total_products = Product.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed termine: {created_count} crees, {updated_count} mis a jour, {total_products} produits."
            )
        )

    def _infer_brand(self, category_slug, name):
        known_brands = ("Pampers", "Fervex", "Humex", "Gaviscon", "Maalox", "Smecta", "Spasfon")
        for brand in known_brands:
            if brand.lower() in name.lower():
                return brand
        return self.CATEGORY_BRANDS.get(category_slug, "MarketPharm")

    def _build_summary(self, category_slug, name):
        category_copy = {
            "bebe": "Reference douce et fiable pour les besoins quotidiens de la petite enfance.",
            "tests": "Solution de depistage rapide pour officines, cabinets et usage professionnel.",
            "masques": "Protection respiratoire pensee pour un usage quotidien intensif.",
            "gants": "Protection medicale confortable avec bonne resistance a l'usage.",
            "consommables": "Essentiel de soin et de petite procedure pour structures de sante.",
            "protection": "Materiel de protection pour pharmacies, laboratoires et soins de proximite.",
            "medicaments": "Reference courante de comptoir avec bon niveau de rotation.",
            "rhume": "Aide au confort respiratoire et a la prise en charge des symptomes saisonniers.",
            "digestion": "Support adapte aux inconforts digestifs frequents.",
            "allergie": "Soulagement simple pour les reactions allergiques du quotidien.",
            "premiers-secours": "Indispensable pour trousse d'urgence et soins de premiere intention.",
            "vitamines": "Complement utile pour soutien tonique et prevention saisonniere.",
            "para-pharmacie": "Soin grand public a forte recurrence d'achat en officine.",
        }
        return f"{name}. {category_copy.get(category_slug, 'Produit professionnel selectionne pour la vente en officine.')}"

    def _infer_unit_label(self, category_slug, name):
        name_lower = name.lower()
        if "boite 100" in name_lower:
            return "Boite de 100"
        if "boite 50" in name_lower:
            return "Boite de 50"
        if "100ml" in name_lower:
            return "Flacon 100 ml"
        if "500ml" in name_lower:
            return "Flacon 500 ml"
        if "30ml" in name_lower:
            return "Flacon 30 ml"
        if "10x10" in name_lower:
            return "Paquet sterile 10x10"
        if "5ml" in name_lower:
            return "Unite 5 ml"
        if "mg" in name_lower:
            return "Boite standard"
        if category_slug in {"masques", "gants", "consommables"}:
            return "Conditionnement pro"
        return "Unite"

    def _infer_low_stock_threshold(self, category_slug):
        if category_slug in {"tests", "medicaments", "rhume"}:
            return 15
        if category_slug in {"masques", "gants", "consommables"}:
            return 25
        return 12

    def _infer_min_order_quantity(self, category_slug, name):
        name_lower = name.lower()
        if category_slug in {"masques", "gants"}:
            return 5
        if "boite" in name_lower:
            return 2
        return 1

    def _infer_expiration_date(self, product_slug, category_slug):
        if product_slug in self.SPECIAL_EXPIRATION_DAYS:
            return date.today() + timedelta(days=self.SPECIAL_EXPIRATION_DAYS[product_slug])
        if category_slug in {"medicaments", "rhume", "digestion", "allergie", "vitamines", "tests"}:
            return date.today() + timedelta(days=180)
        return None
