from decimal import Decimal


def volume_discount_percent(subtotal: Decimal) -> int:
    """Remises type MarketPharm (seuils indicatifs)."""
    t = subtotal
    if t >= Decimal("1500"):
        return 5
    if t >= Decimal("1000"):
        return 4
    if t >= Decimal("500"):
        return 3
    if t >= Decimal("250"):
        return 2
    return 0


def apply_discount(subtotal: Decimal) -> tuple[Decimal, int]:
    pct = volume_discount_percent(subtotal)
    total = (subtotal * (Decimal(100 - pct)) / Decimal(100)).quantize(Decimal("0.01"))
    return total, pct
