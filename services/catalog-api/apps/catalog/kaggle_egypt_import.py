"""
Import Kaggle Egypt drugs.csv : inférence de catégorie (slugs du projet uniquement),
répartition équilibrée pour les noms sans mot-clé, conversion EGP → DZD.
"""
from __future__ import annotations

import re
import unicodedata
from decimal import Decimal

# Règles (ordre = priorité) : mots-clés anglais → slug Category du seed_demo.
# Éviter les termes trop larges (ex. « mg » seul) pour laisser la place à la répartition équilibrée.
_KEYWORD_RULES: tuple[tuple[frozenset[str], str], ...] = (
    (
        frozenset(
            {
                "baby",
                "infant",
                "diaper",
                "pampers",
                "newborn",
                "nursery",
                "teething",
                "formula",
                "lactation",
                "pueric",
            }
        ),
        "bebe",
    ),
    (
        frozenset(
            {
                "test",
                "pregnancy",
                "ovulation",
                "covid",
                "antigen",
                "glycem",
                "glucose",
                "strip",
                "pcr",
                "urinary",
                "rapid test",
                "self-test",
                "diagnostic",
                "blood glucose",
                "lancet",
            }
        ),
        "tests",
    ),
    (
        frozenset(
            {
                "mask",
                "ffp2",
                "kn95",
                "surgical",
                "respirator",
                "face mask",
                "protective mask",
            }
        ),
        "masques",
    ),
    (
        frozenset(
            {
                "glove",
                "nitrile",
                "latex",
                "vinyl",
                "examination glove",
                "powder-free",
                "sterile glove",
            }
        ),
        "gants",
    ),
    (
        frozenset(
            {
                "syringe",
                "compress",
                "bandage",
                "band elastic",
                "consumable",
                "needle",
                "catheter",
                "cannula",
                "infusion",
                "gauze",
                "swab",
                "sterile water",
            }
        ),
        "consommables",
    ),
    (
        frozenset(
            {
                "protection",
                "hydroalcoholic",
                "sanitizer",
                "thermometer infrared",
                "face shield",
                "goggle",
                "ppe",
                "protective equipment",
            }
        ),
        "protection",
    ),
    (
        frozenset(
            {
                "cold",
                "flu",
                "cough",
                "nasal",
                "fever",
                "rhume",
                "sinus",
                "throat",
                "decongestant",
                "expectorant",
            }
        ),
        "rhume",
    ),
    (
        frozenset(
            {
                "gastric",
                "digestion",
                "stomach",
                "acid",
                "laxative",
                "constipation",
                "antiemetic",
                "antacid",
                "proton",
                "bowel",
                "diarrhea",
                "nausea",
                "reflux",
            }
        ),
        "digestion",
    ),
    (
        frozenset(
            {
                "allergy",
                "antihistamine",
                "hay fever",
                "loratadine",
                "cetirizine",
                "histamine",
            }
        ),
        "allergie",
    ),
    (
        frozenset(
            {
                "first aid",
                "disinfect",
                "antiseptic",
                "wound",
                "burn",
                "iodine",
                "hydrogen peroxide",
                "cotton",
                "adhesive",
                "plaster",
                "dressing",
            }
        ),
        "premiers-secours",
    ),
    (
        frozenset(
            {
                "vitamin",
                "omega",
                "collagen",
                "multivitamin",
                "supplement",
                "dietary",
                "mineral",
                "calcium",
                "iron",
                "folic",
                "magnesium",
                "zinc",
                "sachet vitamin",
            }
        ),
        "vitamines",
    ),
    (
        frozenset(
            {
                "cream",
                "shampoo",
                "soap",
                "wash",
                "facial",
                "acne",
                "hair",
                "skin",
                "derma",
                "lotion",
                "gel wash",
                "toothpaste",
                "mouthwash",
                "moisturizer",
                "sunscreen",
                "deodorant",
                "body wash",
                "ointment",
                "eye drop",
                "ear drop",
            }
        ),
        "para-pharmacie",
    ),
    (
        frozenset(
            {
                "tablet",
                "tabs",
                "cap",
                "capsule",
                "supp",
                "vial",
                "injection",
                "syrup",
                "sachet",
                "antibiotic",
                "diabetes",
                "insulin",
                "antiviral",
                "antipsychotic",
                "analgesic",
                "antipyretic",
                "antidepressant",
                "anticoagulant",
                "antifungal",
                "anthelmintic",
                "bronchitis",
                "osteoporosis",
                "hypertension",
                "inhaler",
                "spray",
                "penicillin",
                "penem",
            }
        ),
        "medicaments",
    ),
)


def _normalize_name_for_match(name: str) -> str:
    s = unicodedata.normalize("NFC", name).lower()
    s = re.sub(r"[^\w\s|]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _keyword_in_hay(hay: str, kw: str) -> bool:
    if " " in kw:
        return kw in hay
    return re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?![a-z0-9])", hay, re.I) is not None


def infer_category_slug(name: str, allowed_slugs: frozenset[str]) -> str:
    """Sans compteur : premier mot-clé trouvé, sinon médicaments ou premier slug."""
    if not allowed_slugs:
        raise ValueError("Aucune catégorie en base")
    hay = _normalize_name_for_match(name)
    for keywords, slug in _KEYWORD_RULES:
        if slug not in allowed_slugs:
            continue
        for kw in keywords:
            if _keyword_in_hay(hay, kw):
                return slug
    if "medicaments" in allowed_slugs:
        return "medicaments"
    return sorted(allowed_slugs)[0]


def assign_category_for_import(
    name: str,
    allowed_slugs: frozenset[str],
    counts: dict[str, int],
) -> tuple[str, str]:
    """
    Assigne une catégorie : règles par mots-clés, sinon catégorie la moins remplie
    (répartition équilibrée sur tout le catalogue).

    Retourne (slug, 'rule' | 'balanced').
    """
    if not allowed_slugs:
        raise ValueError("Aucune catégorie en base")

    hay = _normalize_name_for_match(name)
    for keywords, slug in _KEYWORD_RULES:
        if slug not in allowed_slugs:
            continue
        for kw in keywords:
            if _keyword_in_hay(hay, kw):
                counts[slug] = counts.get(slug, 0) + 1
                return slug, "rule"

    slug = min(allowed_slugs, key=lambda s: (counts.get(s, 0), s))
    counts[slug] = counts.get(slug, 0) + 1
    return slug, "balanced"


def egp_to_dzd(amount_egp: Decimal, rate: Decimal) -> Decimal:
    """Convertit un montant EGP en DZD (taux EGP→DZD : combien de DZD pour 1 EGP)."""
    return (amount_egp * rate).quantize(Decimal("0.01"))
