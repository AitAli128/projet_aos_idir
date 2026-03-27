import base64
import json
from django.conf import settings

from .views import _is_admin

def public_endpoints(request):
    lang = request.session.get("lang", "fr")
    texts = {
        "fr": {
            "brand": "MarketPharm",
            "tagline": "Pharmacie & parapharmacie pour professionnels",
            "catalog": "Catalogue",
            "cart": "Panier",
            "orders": "Mes commandes",
            "login": "Connexion",
            "logout": "Déconnexion",
            "search_placeholder": "Recherche produit...",
            "min_stock": "Stock min",
            "all_categories": "Toutes catégories",
            "filter": "Filtrer",
            "empty_cart": "Panier vide",
            "checkout": "Commander",
            "no_orders": "Aucune commande pour le moment.",
        },
        "ar": {
            "brand": "ماركت فارم",
            "tagline": "صيدلية وبارافارما للمحترفين",
            "catalog": "الكتالوج",
            "cart": "سلة التسوق",
            "orders": "طلباتي",
            "login": "تسجيل الدخول",
            "logout": "تسجيل الخروج",
            "search_placeholder": "بحث عن منتج...",
            "min_stock": "الحد الأدنى للمخزون",
            "all_categories": "جميع الفئات",
            "filter": "تصفية",
            "empty_cart": "السلة فارغة",
            "checkout": "إنهاء الطلب",
            "no_orders": "لا توجد طلبات حتى الآن.",
        },
    }
    active_text = texts.get(lang, texts["fr"])
    
    # Extraire les infos de l'utilisateur depuis le JWT
    user_name = "Utilisateur Pro"
    user_id_display = "N/A"
    user_initials = "P"
    user_is_admin_flag = _is_admin(request)
    
    token = request.session.get("access")
    if token:
        try:
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.urlsafe_b64decode(payload)
                data = json.loads(decoded)
                
                extracted_name = data.get('last_name') or data.get('first_name') or data.get('name')
                if data.get('first_name') and data.get('last_name'):
                    extracted_name = f"{data['first_name']} {data['last_name']}"
                if extracted_name:
                    user_name = extracted_name
                elif data.get('email'):
                    user_name = data['email']
                
                extracted_id = data.get('user_id') or data.get('id')
                if extracted_id:
                    user_id_display = str(extracted_id)
                
                if extracted_name:
                    name_str = str(extracted_name)
                    parts_name = name_str.split()
                    initials = ""
                    if len(parts_name) > 0 and len(parts_name[0]) > 0:
                        initials += parts_name[0][0].upper()
                    if len(parts_name) > 1 and len(parts_name[1]) > 0:
                        initials += parts_name[1][0].upper()
                    if initials:
                        user_initials = initials
        except:
            pass

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
    }
