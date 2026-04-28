from datetime import datetime, timedelta


CATEGORY_IMAGE_MAP = {
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


def decorate_product(product):
    item = dict(product or {})
    category_slug = item.get("category_slug") or ""
    stock = int(item.get("stock") or 0)
    threshold = int(item.get("low_stock_threshold") or 12)
    item["image_url"] = item.get("image_url") or CATEGORY_IMAGE_MAP.get(category_slug, "/static/img/logo.png")
    item["brand"] = item.get("brand") or "MarketPharm"
    item["unit_label"] = item.get("unit_label") or "Unite"
    item["min_order_quantity"] = int(item.get("min_order_quantity") or 1)
    item["order_hint"] = (
        f"Minimum {item['min_order_quantity']} unites" if item["min_order_quantity"] > 1 else "Commande libre"
    )

    if stock <= 0:
        item["stock_state"] = "out"
        item["stock_label"] = "Rupture"
        item["stock_badge_class"] = "badge-out"
    elif stock <= threshold:
        item["stock_state"] = "low"
        item["stock_label"] = f"Plus que {stock}"
        item["stock_badge_class"] = "badge-low"
    else:
        item["stock_state"] = "ok"
        item["stock_label"] = f"{stock} en stock"
        item["stock_badge_class"] = "badge-ok"

    expiration_date = item.get("expiration_date")
    item["expired"] = False
    item["expiring_soon"] = bool(item.get("is_expiring_soon"))
    if expiration_date:
        try:
            parsed = datetime.strptime(expiration_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            item["expired"] = parsed < today
            if not item["expired"]:
                item["expiring_soon"] = parsed <= today + timedelta(days=45)
        except ValueError:
            item["expired"] = False
            item["expiring_soon"] = False

    return item


def decorate_products(products):
    return [decorate_product(product) for product in products or []]


def build_catalog_metrics(products, categories):
    items = decorate_products(products)
    return {
        "total_products": len(items),
        "featured_count": len([item for item in items if item.get("is_featured")]),
        "low_stock_count": len([item for item in items if item.get("stock_state") == "low"]),
        "out_of_stock_count": len([item for item in items if item.get("stock_state") == "out"]),
        "expiring_count": len([item for item in items if item.get("expiring_soon")]),
        "category_count": len(categories or []),
    }
