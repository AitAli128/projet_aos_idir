"""
Import produits depuis un CSV (ex. export Kaggle).

Gère encodage UTF-8 / UTF-8-sig, troncature des champs selon max_length,
génération de slugs uniques, prix avec virgule ou point, SKU auto si absent.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.catalog.models import Category, Product


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _clean_str(value: str | None) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    s = unicodedata.normalize("NFC", s)
    return s


def _parse_decimal(raw: str, *, price_in_cents: bool) -> Decimal:
    s = _clean_str(raw)
    if not s:
        raise ValueError("prix vide")
    s = s.replace(" ", "").replace("\u00a0", "")
    s = re.sub(r"^[€$£]\s*", "", s)
    # Suffixes / codes devise courants (CSV Kaggle, exports locaux)
    s = re.sub(
        r"\s*(?:DA|DZD|EGP|E£|EUR|€|USD|\$|ج\.م|L\.?E\.?|LE)\s*$",
        "",
        s,
        flags=re.IGNORECASE,
    )
    s = s.replace(",", ".")
    # dernier point = décimal si plusieurs points
    if s.count(".") > 1:
        parts = s.split(".")
        s = "".join(parts[:-1]) + "." + parts[-1]
    try:
        d = Decimal(s)
    except InvalidOperation as e:
        raise ValueError(f"prix invalide: {raw!r}") from e
    if price_in_cents:
        d = d / Decimal("100")
    if d <= 0:
        raise ValueError(f"prix doit être > 0, obtenu: {d}")
    return d.quantize(Decimal("0.01"))


def _parse_int(raw: str | None, default: int = 0) -> int:
    if raw is None or str(raw).strip() == "":
        return default
    s = _clean_str(str(raw)).replace(" ", "").replace(",", ".")
    try:
        return max(0, int(round(float(s))))
    except ValueError:
        return default


def _unique_slug(base: str, *, exclude_pk: int | None = None) -> str:
    base_slug = slugify(base) or "produit"
    base_slug = _truncate(base_slug, 200)
    slug = base_slug
    n = 1
    qs = Product.objects.filter(slug=slug)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    while qs.exists():
        suffix = f"-{n}"
        slug = _truncate(base_slug[: 200 - len(suffix)] + suffix, 200)
        n += 1
        qs = Product.objects.filter(slug=slug)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
    return slug


class Command(BaseCommand):
    help = "Importe des produits depuis un fichier CSV (colonnes configurables)."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Chemin vers le fichier .csv")
        parser.add_argument(
            "--encoding",
            default="utf-8-sig",
            help="Encodage (utf-8-sig enlève le BOM Excel ; utf-8 pour fichiers bruts)",
        )
        parser.add_argument("--delimiter", default=",", help="Séparateur de colonnes (, ou ;)")
        parser.add_argument(
            "--col-name",
            default="name",
            help="Nom de la colonne libellé produit (adapter au CSV Kaggle)",
        )
        parser.add_argument("--col-price", default="price", help="Colonne prix")
        parser.add_argument("--col-sku", default="sku", help="Colonne SKU / code (optionnel)")
        parser.add_argument(
            "--col-category",
            default="category",
            help="Colonne catégorie (slug ou nom ; optionnel si --default-category-slug)",
        )
        parser.add_argument(
            "--col-summary",
            default="summary",
            help="Colonne description courte / longue (optionnel)",
        )
        parser.add_argument("--col-stock", default="stock", help="Colonne stock (optionnel)")
        parser.add_argument(
            "--default-category-slug",
            default="medicaments",
            help="Slug Category si la ligne n’a pas de catégorie ou colonne absente",
        )
        parser.add_argument(
            "--price-in-cents",
            action="store_true",
            help="Interpréter le prix en centimes (ex. 199 = 1,99)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Valider et afficher les erreurs sans écrire en base",
        )
        parser.add_argument(
            "--start-row",
            type=int,
            default=1,
            help="Indice 1-based de la première ligne de données (après l’en-tête)",
        )
        parser.add_argument(
            "--max-rows",
            type=int,
            default=None,
            help="Limiter le nombre de lignes importées (tests)",
        )
        parser.add_argument(
            "--sku-prefix",
            default="CSV",
            help="Préfixe si la colonne SKU est absente (ex. EGP pour le jeu Égypte Kaggle)",
        )

    def handle(self, *args, **options):
        path = Path(options["csv_file"]).expanduser().resolve()
        if not path.is_file():
            raise CommandError(f"Fichier introuvable: {path}")

        enc = options["encoding"]
        delim = options["delimiter"]
        col_name = options["col_name"]
        col_price = options["col_price"]
        col_sku = options["col_sku"]
        col_cat = options["col_category"]
        col_sum = options["col_summary"]
        col_stock = options["col_stock"]
        default_slug = options["default_category_slug"]
        price_in_cents = options["price_in_cents"]
        dry = options["dry_run"]
        sku_prefix = options["sku_prefix"]

        try:
            default_cat = Category.objects.get(slug=default_slug)
        except Category.DoesNotExist as e:
            raise CommandError(
                f'Catégorie par défaut "{default_slug}" absente. '
                f"Lancez d’abord: python manage.py seed_demo"
            ) from e

        def strip_row(row: dict) -> dict:
            return {(k.strip() if k else k): v for k, v in row.items()}

        with path.open("r", encoding=enc, newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            if not reader.fieldnames:
                raise CommandError("CSV sans en-tête")

            headers = [h.strip() for h in reader.fieldnames if h]
            missing = [c for c in (col_name, col_price) if c not in headers]
            if missing:
                raise CommandError(
                    f"Colonnes manquantes: {missing}. Colonnes trouvées: {headers}"
                )

        created = updated = skipped = dry_preview = 0
        errors: list[str] = []
        row_num = 1
        consumed = 0

        with path.open("r", encoding=enc, newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            for row in reader:
                row = strip_row(row)
                row_num += 1
                if row_num - 1 < options["start_row"]:
                    continue
                if options["max_rows"] is not None and consumed >= options["max_rows"]:
                    break

                raw_name = row.get(col_name, "")
                name = _clean_str(raw_name)
                if not name:
                    skipped += 1
                    continue

                if len(name) > 500:
                    self.stdout.write(
                        self.style.WARNING(f"Ligne {row_num}: nom tronqué ({len(name)} → 500 car.)")
                    )
                    name = _truncate(name, 500)

                raw_price = row.get(col_price, "")
                try:
                    price = _parse_decimal(raw_price, price_in_cents=price_in_cents)
                except ValueError as e:
                    errors.append(f"Ligne {row_num}: {e}")
                    skipped += 1
                    continue

                if col_sku in row and _clean_str(row.get(col_sku)):
                    sku = _clean_str(row[col_sku])
                else:
                    sku = f"{sku_prefix}-{row_num}"

                if len(sku) > 128:
                    self.stdout.write(
                        self.style.WARNING(f"Ligne {row_num}: SKU tronqué ({len(sku)} → 128)")
                    )
                    sku = _truncate(sku, 128)

                summary = ""
                if col_sum in row:
                    summary = _clean_str(row.get(col_sum, ""))
                # TextField : pas de limite stricte côté modèle ; éviter abus mémoire
                if len(summary) > 2_000_000:
                    summary = summary[:2_000_000] + "\n…"

                stock = 0
                if col_stock in row:
                    stock = _parse_int(row.get(col_stock), 0)

                category = default_cat
                if col_cat in row and _clean_str(row.get(col_cat, "")):
                    cat_val = _clean_str(row[col_cat])
                    cat = Category.objects.filter(slug__iexact=slugify(cat_val)).first()
                    if not cat:
                        cat = Category.objects.filter(name__iexact=cat_val).first()
                    if not cat:
                        cat = Category.objects.filter(name__icontains=cat_val[:40]).first()
                    if cat:
                        category = cat
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Ligne {row_num}: catégorie {cat_val!r} introuvable → {default_cat.slug}"
                            )
                        )

                if dry:
                    self.stdout.write(
                        f"[dry-run] {name[:60]}… | {price} | {sku} | cat={category.slug}"
                    )
                    dry_preview += 1
                    consumed += 1
                    continue

                product = Product.objects.filter(sku=sku).first()
                if product:
                    product.name = name
                    product.category = category
                    product.summary = summary
                    product.price = price
                    product.stock = stock
                    product.slug = _unique_slug(name, exclude_pk=product.pk)
                    product.save()
                    updated += 1
                    consumed += 1
                else:
                    slug = _unique_slug(name)
                    Product.objects.create(
                        name=name,
                        slug=slug,
                        category=category,
                        summary=summary,
                        price=price,
                        stock=stock,
                        sku=sku,
                    )
                    created += 1
                    consumed += 1

        msg = (
            f"Terminé — créés: {created}, mis à jour: {updated}, ignorés: {skipped}"
            + (f", aperçu dry-run: {dry_preview}" if dry else "")
        )
        self.stdout.write(self.style.SUCCESS(msg))
        if errors:
            self.stdout.write(self.style.ERROR(f"{len(errors)} erreur(s) de parsing prix:"))
            for err in errors[:50]:
                self.stdout.write(self.style.ERROR(f"  {err}"))
            if len(errors) > 50:
                self.stdout.write(self.style.ERROR(f"  … et {len(errors) - 50} autres"))
