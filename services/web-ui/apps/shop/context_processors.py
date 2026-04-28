import base64
import json

from django.conf import settings

from .service_registry import get_service_status
from .views import _is_admin


def public_endpoints(request):
    lang = request.session.get("lang", "fr")
    texts = {
        "fr": {
            "brand": "MarketPharm",
            "tagline": "Approvisionnement pharmacie et para pour professionnels",
            "catalog": "Catalogue",
            "cart": "Panier",
            "orders": "Mes commandes",
            "login": "Connexion",
            "logout": "Deconnexion",
            "search_placeholder": "Recherche produit...",
            "min_stock": "Stock min",
            "all_categories": "Toutes categories",
            "filter": "Filtrer",
            "empty_cart": "Panier vide",
            "checkout": "Commander",
            "no_orders": "Aucune commande pour le moment.",
        },
        "ar": {
            "brand": "MarketPharm",
            "tagline": "منصة صيدلية ومستلزمات للمحترفين",
            "catalog": "الكتالوج",
            "cart": "السلة",
            "orders": "طلباتي",
            "login": "تسجيل الدخول",
            "logout": "تسجيل الخروج",
            "search_placeholder": "ابحث عن منتج...",
            "min_stock": "الحد الادنى",
            "all_categories": "كل الفئات",
            "filter": "تصفية",
            "empty_cart": "السلة فارغة",
            "checkout": "اتمام الطلب",
            "no_orders": "لا توجد طلبات حاليا.",
        },
    }
    active_text = texts.get(lang, texts["fr"])

    user_name = "Utilisateur Pro"
    user_id_display = "N/A"
    user_initials = "P"
    user_is_admin_flag = _is_admin(request)
    token = request.session.get("access")
    cart = request.session.get("cart") or {}
    cart_item_count = sum(int(value) for value in cart.values() if str(value).isdigit())

    if token:
        try:
            parts = token.split(".")
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += "=" * padding
                decoded = base64.urlsafe_b64decode(payload)
                data = json.loads(decoded)
                extracted_name = data.get("last_name") or data.get("first_name") or data.get("name")
                if data.get("first_name") and data.get("last_name"):
                    extracted_name = f"{data['first_name']} {data['last_name']}"
                if extracted_name:
                    user_name = extracted_name
                elif data.get("email"):
                    user_name = data["email"]

                extracted_id = data.get("user_id") or data.get("id")
                if extracted_id:
                    user_id_display = str(extracted_id)

                if extracted_name:
                    parts_name = str(extracted_name).split()
                    initials = ""
                    if parts_name and parts_name[0]:
                        initials += parts_name[0][0].upper()
                    if len(parts_name) > 1 and parts_name[1]:
                        initials += parts_name[1][0].upper()
                    if initials:
                        user_initials = initials
        except Exception:
            pass

    service_statuses = [
        get_service_status(settings.AUTH_SERVICE_NAME, settings.AUTH_INTERNAL_URL, "Authentification"),
        get_service_status(settings.API_SERVICE_NAME, settings.API_INTERNAL_URL, "Catalogue"),
    ]

    return {
        "PUBLIC_AUTH_URL": settings.PUBLIC_AUTH_URL,
        "PUBLIC_API_URL": settings.PUBLIC_API_URL,
        "LANG": lang,
        "DIR": "rtl" if lang == "ar" else "ltr",
        "T": active_text,
        "user_is_admin": user_is_admin_flag,
        "user_name": user_name,
        "user_id_display": user_id_display,
        "user_initials": user_initials,
        "cart_item_count": cart_item_count,
        "service_statuses": service_statuses,
        "platform_degraded": any(not service["available"] for service in service_statuses),
    }
