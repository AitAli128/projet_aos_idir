"""
Import drugs.csv (Kaggle Égypte) : catégories = uniquement celles du projet (inférence),
prix EGP → DZD (taux configurable), SKU DZD-<ligne>.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.catalog.kaggle_egypt_import import assign_category_for_import, egp_to_dzd
from apps.catalog.management.commands.import_products_csv import (
    _clean_str,
    _parse_decimal,
    _parse_int,
    _truncate,
    _unique_slug,
)
from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = (
        "Importe data/imports/drugs_egypt.csv : catégories inférées (slugs existants), "
        "prix convertis EGP → DZD (EGP_TO_DZD_RATE)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validation sans écriture en base",
        )
        parser.add_argument(
            "--max-rows",
            type=int,
            default=None,
            help="Limiter le nombre de lignes (tests)",
        )

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / "data" / "imports" / "drugs_egypt.csv"
        if not csv_path.is_file():
            raise CommandError(
                f"Fichier absent: {csv_path}\n"
                "Copiez drugs.csv (Kaggle) vers ce chemin."
            )

        rate = getattr(settings, "EGP_TO_DZD_RATE", None)
        if rate is None:
            raise CommandError(
                "EGP_TO_DZD_RATE manquant dans settings (voir .env : combien de DZD pour 1 EGP)."
            )
        rate = Decimal(str(rate))
        if rate <= 0:
            raise CommandError("EGP_TO_DZD_RATE doit être > 0")

        allowed_slugs = frozenset(Category.objects.values_list("slug", flat=True))
        if not allowed_slugs:
            raise CommandError(
                "Aucune catégorie en base. Lancez : python manage.py seed_demo"
            )

        # Compteur pour répartition équilibrée (produits sans mot-clé reconnu)
        category_counts: dict[str, int] = {s: 0 for s in allowed_slugs}

        dry = options["dry_run"]
        max_rows = options["max_rows"]
        created = updated = skipped = 0
        row_num = 1
        consumed = 0
        balanced_n = rule_n = 0

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            headers = [h.strip() for h in (reader.fieldnames or []) if h]
            for req in ("name", "price_EGP"):
                if req not in headers:
                    raise CommandError(f"Colonne requise absente: {req}. Trouvées: {headers}")

            for row in reader:
                row = {(k.strip() if k else k): v for k, v in row.items()}
                row_num += 1

                name = _clean_str(row.get("name", ""))
                if not name:
                    skipped += 1
                    continue
                if len(name) > 500:
                    name = _truncate(name, 500)

                if max_rows is not None and consumed >= max_rows:
                    break

                try:
                    price_egp = _parse_decimal(row.get("price_EGP", ""), price_in_cents=False)
                except ValueError:
                    skipped += 1
                    continue

                price_dzd = egp_to_dzd(price_egp, rate)
                stock = _parse_int(row.get("stock"), 0)
                sku = f"DZD-{row_num}"

                slug_cat, src = assign_category_for_import(name, allowed_slugs, category_counts)
                if src == "balanced":
                    balanced_n += 1
                else:
                    rule_n += 1
                category = Category.objects.get(slug=slug_cat)

                summary_parts = [
                    "Produit pharmaceutique certifié et validé pour le catalogue.",
                    "Catégorie : mots-clés."
                    if src == "rule"
                    else "Catégorie : sélection standardisée.",
                ]
                summary = " ".join(summary_parts)

                if dry:
                    self.stdout.write(
                        f"[dry-run] {name[:55]}… | {price_dzd} DZD | {slug_cat} ({src}) | {sku}"
                    )
                    consumed += 1
                    continue

                product = Product.objects.filter(sku=sku).first()
                if product:
                    product.name = name
                    product.category = category
                    product.summary = summary
                    product.price = price_dzd
                    product.stock = stock
                    product.slug = _unique_slug(name, exclude_pk=product.pk)
                    product.save()
                    updated += 1
                else:
                    Product.objects.create(
                        name=name,
                        slug=_unique_slug(name),
                        category=category,
                        summary=summary,
                        price=price_dzd,
                        stock=stock,
                        sku=sku,
                    )
                    created += 1
                consumed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Terminé — créés: {created}, mis à jour: {updated}, ignorés: {skipped}"
                + (" (dry-run)" if dry else "")
                + f" | taux EGP→DZD: {rate}"
                + f" | par mots-clés: {rule_n}, répartition équilibrée: {balanced_n}"
            )
        )
        self.stdout.write("Répartition par catégorie (après import) :")
        for s in sorted(category_counts.keys()):
            self.stdout.write(f"  {s}: {category_counts[s]}")
