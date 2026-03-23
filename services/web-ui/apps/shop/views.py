from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from requests import HTTPError, RequestException

from . import api_client

EXCHANGE_RATE = getattr(settings, "EXCHANGE_RATE", 240)

# ------------------------------------------------------------
# Liste statique des médicaments (prix déjà en dinars)
# ------------------------------------------------------------
STATIC_MEDICATIONS = [
    {'id': 1001, 'name': 'Doliprane 500 mg', 'category_name': 'Douleur / Fièvre', 'price_dzd': 40, 'summary': 'Antalgique, fièvre', 'icon': 'fa-tablets'},
    {'id': 1002, 'name': 'Doliprane 1000 mg', 'category_name': 'Douleur / Fièvre', 'price_dzd': 580, 'summary': 'Antalgique fort', 'icon': 'fa-tablets'},
    {'id': 1003, 'name': 'Doliprane 150 mg sachet', 'category_name': 'Douleur / Fièvre', 'price_dzd': 105, 'summary': 'Sachet pour enfant', 'icon': 'fa-prescription-bottle'},
    {'id': 1004, 'name': 'Doliprane 300 mg sachet', 'category_name': 'Douleur / Fièvre', 'price_dzd': 120, 'summary': 'Sachet pour enfant', 'icon': 'fa-prescription-bottle'},
    {'id': 1005, 'name': 'Doliprane 100 mg sachet', 'category_name': 'Douleur / Fièvre', 'price_dzd': 110, 'summary': 'Sachet pour enfant', 'icon': 'fa-prescription-bottle'},
    {'id': 1006, 'name': 'Doliprane 100 mg suppo', 'category_name': 'Douleur / Fièvre', 'price_dzd': 100, 'summary': 'Suppositoire', 'icon': 'fa-capsules'},
    {'id': 1007, 'name': 'Doliprane 150 mg suppo', 'category_name': 'Douleur / Fièvre', 'price_dzd': 102, 'summary': 'Suppositoire', 'icon': 'fa-capsules'},
    {'id': 1008, 'name': 'Doliprane 300 mg suppo', 'category_name': 'Douleur / Fièvre', 'price_dzd': 110, 'summary': 'Suppositoire', 'icon': 'fa-capsules'},
    {'id': 1009, 'name': 'Paracetamol générique', 'category_name': 'Douleur / Fièvre', 'price_dzd': 45, 'summary': 'Générique', 'icon': 'fa-tablets'},
    {'id': 1010, 'name': 'Dafalgan', 'category_name': 'Douleur / Fièvre', 'price_dzd': 115, 'summary': 'Antalgique', 'icon': 'fa-tablets'},
    {'id': 1011, 'name': 'Ibuprofen', 'category_name': 'Anti-inflammatoire', 'price_dzd': 150, 'summary': 'Anti-inflammatoire', 'icon': 'fa-capsules'},
    {'id': 1012, 'name': 'Nurofen', 'category_name': 'Anti-inflammatoire', 'price_dzd': 325, 'summary': 'Anti-inflammatoire', 'icon': 'fa-capsules'},
    {'id': 1013, 'name': 'Ketoprofen gel', 'category_name': 'Anti-inflammatoire', 'price_dzd': 225, 'summary': 'Gel topique', 'icon': 'fa-hand-holding-medical'},
    {'id': 1014, 'name': 'Aspirine UPSA', 'category_name': 'Anti-inflammatoire', 'price_dzd': 75, 'summary': 'Antalgique, fièvre', 'icon': 'fa-tablets'},
    {'id': 1015, 'name': 'Aspegic', 'category_name': 'Anti-inflammatoire', 'price_dzd': 65, 'summary': 'Sachet', 'icon': 'fa-prescription-bottle'},
    {'id': 1016, 'name': 'Fervex', 'category_name': 'Rhume / Grippe', 'price_dzd': 275, 'summary': 'Rhume, grippe', 'icon': 'fa-head-side-mask'},
    {'id': 1017, 'name': 'Dolirhume', 'category_name': 'Rhume / Grippe', 'price_dzd': 240, 'summary': 'Rhume', 'icon': 'fa-head-side-mask'},
    {'id': 1018, 'name': 'Humex', 'category_name': 'Rhume / Grippe', 'price_dzd': 275, 'summary': 'Rhume', 'icon': 'fa-head-side-mask'},
    {'id': 1019, 'name': 'Rhinadvil', 'category_name': 'Rhume / Grippe', 'price_dzd': 400, 'summary': 'Rhume, douleur', 'icon': 'fa-capsules'},
    {'id': 1020, 'name': 'Actifed', 'category_name': 'Rhume / Grippe', 'price_dzd': 325, 'summary': 'Rhume', 'icon': 'fa-capsules'},
    {'id': 1021, 'name': 'Cetirizine', 'category_name': 'Allergie', 'price_dzd': 115, 'summary': 'Antihistaminique', 'icon': 'fa-allergies'},
    {'id': 1022, 'name': 'Loratadine', 'category_name': 'Allergie', 'price_dzd': 160, 'summary': 'Antihistaminique', 'icon': 'fa-allergies'},
    {'id': 1023, 'name': 'Desloratadine', 'category_name': 'Allergie', 'price_dzd': 275, 'summary': 'Antihistaminique', 'icon': 'fa-allergies'},
    {'id': 1024, 'name': 'Aerius', 'category_name': 'Allergie', 'price_dzd': 400, 'summary': 'Antihistaminique', 'icon': 'fa-allergies'},
    {'id': 1025, 'name': 'Clarityne', 'category_name': 'Allergie', 'price_dzd': 325, 'summary': 'Antihistaminique', 'icon': 'fa-allergies'},
    {'id': 1026, 'name': 'Toplexil', 'category_name': 'Toux / Gorge', 'price_dzd': 275, 'summary': 'Toux sèche', 'icon': 'fa-lungs'},
    {'id': 1027, 'name': 'Fluimucil', 'category_name': 'Toux / Gorge', 'price_dzd': 325, 'summary': 'Toux grasse', 'icon': 'fa-lungs'},
    {'id': 1028, 'name': 'Exomuc', 'category_name': 'Toux / Gorge', 'price_dzd': 325, 'summary': 'Toux grasse', 'icon': 'fa-lungs'},
    {'id': 1029, 'name': 'Mucomyst', 'category_name': 'Toux / Gorge', 'price_dzd': 275, 'summary': 'Toux grasse', 'icon': 'fa-lungs'},
    {'id': 1030, 'name': 'Maxilase', 'category_name': 'Toux / Gorge', 'price_dzd': 375, 'summary': 'Maux de gorge', 'icon': 'fa-stethoscope'},
    {'id': 1031, 'name': 'Strepsils', 'category_name': 'Toux / Gorge', 'price_dzd': 250, 'summary': 'Pastilles gorge', 'icon': 'fa-candy-cane'},
    {'id': 1032, 'name': 'Hexaspray', 'category_name': 'Toux / Gorge', 'price_dzd': 425, 'summary': 'Spray gorge', 'icon': 'fa-spray-can'},
    {'id': 1033, 'name': 'Smecta', 'category_name': 'Digestion / Estomac', 'price_dzd': 200, 'summary': 'Diarhée', 'icon': 'fa-stomach'},
    {'id': 1034, 'name': 'Gaviscon', 'category_name': 'Digestion / Estomac', 'price_dzd': 400, 'summary': 'Reflux', 'icon': 'fa-stomach'},
    {'id': 1035, 'name': 'Spasfon', 'category_name': 'Digestion / Estomac', 'price_dzd': 275, 'summary': 'Spasmes', 'icon': 'fa-stomach'},
    {'id': 1036, 'name': 'Imodium', 'category_name': 'Digestion / Estomac', 'price_dzd': 325, 'summary': 'Diarhée', 'icon': 'fa-stomach'},
    {'id': 1037, 'name': 'Rennie', 'category_name': 'Digestion / Estomac', 'price_dzd': 275, 'summary': 'Brûlures', 'icon': 'fa-stomach'},
    {'id': 1038, 'name': 'Meteospasmyl', 'category_name': 'Digestion / Estomac', 'price_dzd': 500, 'summary': 'Ballonnements', 'icon': 'fa-stomach'},
    {'id': 1039, 'name': 'Vitamine C (Cevit)', 'category_name': 'Vitamines', 'price_dzd': 85, 'summary': 'Vitamine C', 'icon': 'fa-apple-alt'},
    {'id': 1040, 'name': 'Supradyn', 'category_name': 'Vitamines', 'price_dzd': 600, 'summary': 'Multivitamines', 'icon': 'fa-apple-alt'},
]

# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------
def _token(request):
    return request.session.get("access")

def to_dzd(price_eur):
    """Convertit un prix en euros en dinars algériens."""
    return price_eur * EXCHANGE_RATE

# ------------------------------------------------------------
# Vues publiques
# ------------------------------------------------------------
def home(request):
    try:
        data = api_client.api_get("products/", token=None)
        products = data.get("results", data) if isinstance(data, dict) else data
        if isinstance(products, list):
            featured = products[:6]
            for p in featured:
                p["price_dzd"] = to_dzd(p.get("price", 0))
        else:
            featured = []
    except Exception:
        # Fallback sur les médicaments statiques
        featured = STATIC_MEDICATIONS[:6]
    return render(request, "shop/home.html", {"featured_products": featured})

def login_view(request):
    if _token(request):
        return redirect("catalog")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        try:
            data = api_client.auth_token(email=email, password=password)
        except HTTPError:
            messages.error(request, "E-mail ou mot de passe incorrect.")
            return render(request, "shop/login.html")
        except RequestException:
            messages.error(request, "Impossible de joindre le service d’authentification.")
            return render(request, "shop/login.html")
        request.session["access"] = data.get("access")
        request.session["refresh"] = data.get("refresh")
        messages.success(request, "Connexion réussie.")
        next_url = request.GET.get("next") or reverse("catalog")
        return redirect(next_url)
    return render(request, "shop/login.html")

def logout_view(request):
    request.session.flush()
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("home")

def signup_view(request):
    if _token(request):
        return redirect("catalog")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        # Validations simples
        if not full_name or not email or not password:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, "shop/signup.html")

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "shop/signup.html")

        try:
            # Appel à l'API d'inscription (à adapter selon votre endpoint)
            response = api_client.api_post("register/", token=None, data={
                "full_name": full_name,
                "email": email,
                "password": password,
            })
        except HTTPError as e:
            # Si l'API renvoie une erreur, on affiche le message d'erreur
            messages.error(request, f"Erreur lors de l'inscription : {str(e)}")
            return render(request, "shop/signup.html")
        except RequestException:
            messages.error(request, "Impossible de joindre le service d'authentification.")
            return render(request, "shop/signup.html")

        # Normalement l'API renvoie les tokens après inscription
        # Si votre API ne renvoie pas directement les tokens, vous pouvez appeler la connexion après
        try:
            # On suppose que la réponse contient access et refresh
            access_token = response.get("access")
            refresh_token = response.get("refresh")
        except AttributeError:
            # Si l'API n'a pas retourné les tokens, on peut tenter une connexion automatique
            try:
                login_data = api_client.auth_token(email=email, password=password)
                access_token = login_data.get("access")
                refresh_token = login_data.get("refresh")
            except:
                messages.error(request, "Compte créé mais impossible de vous connecter automatiquement. Veuillez vous connecter manuellement.")
                return redirect("login")

        # Stocker les tokens en session
        request.session["access"] = access_token
        request.session["refresh"] = refresh_token

        messages.success(request, f"Bienvenue {full_name} ! Votre compte a été créé avec succès.")
        return redirect("catalog")

    return render(request, "shop/signup.html")

# ------------------------------------------------------------
# Vues protégées (nécessitent authentification)
# ------------------------------------------------------------
def _require_auth(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    return None

def catalog(request):
    redir = _require_auth(request)
    if redir:
        return redir
    try:
        data = api_client.api_get("products/", _token(request))
    except RequestException:
        messages.error(request, "Catalogue indisponible, affichage des produits de démonstration.")
        return render(request, "shop/catalog.html", {"results": STATIC_MEDICATIONS})

    if isinstance(data, dict) and "results" in data:
        api_products = data["results"]
    elif isinstance(data, list):
        api_products = data
    else:
        api_products = []

    for p in api_products:
        p["price_dzd"] = to_dzd(p.get("price", 0))

    # Fusion avec les produits statiques pour éviter les doublons (id)
    all_products = {str(p["id"]): p for p in api_products}
    for med in STATIC_MEDICATIONS:
        if str(med["id"]) not in all_products:
            all_products[str(med["id"])] = med

    results = list(all_products.values())
    return render(request, "shop/catalog.html", {"results": results})

# ------------------------------------------------------------
# Panier
# ------------------------------------------------------------
def _get_cart(request) -> dict[str, int]:
    cart = request.session.get("cart") or {}
    out = {}
    for k, v in cart.items():
        try:
            out[str(int(k))] = max(1, int(v))
        except (TypeError, ValueError):
            continue
    request.session["cart"] = out
    return out

def cart_add(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    product_id = request.POST.get("product_id")
    if not product_id:
        messages.error(request, "Produit non spécifié.")
        return redirect("catalog")
    qty_raw = request.POST.get("quantity", "1")
    try:
        quantity = max(1, int(qty_raw))
    except (TypeError, ValueError):
        quantity = 1
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    request.session["cart"] = cart
    messages.success(request, f"{quantity} produit(s) ajouté(s) au panier.")
    return redirect("cart")

def cart_update(request, product_id):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    key = str(product_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "increment":
            cart[key] = cart.get(key, 0) + 1
        elif action == "decrement":
            cart[key] = max(1, cart.get(key, 1) - 1)
        else:
            try:
                qty = int(request.POST.get("quantity", 1))
                cart[key] = max(1, qty)
            except:
                pass
        request.session["cart"] = cart
    return redirect("cart")

def cart_remove(request, product_id):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    messages.info(request, "Produit retiré du panier.")
    return redirect("cart")

def cart_view(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    lines = []
    total_dzd = 0
    token = _token(request)
    for pid, qty in cart.items():
        # Chercher d'abord dans l'API, sinon dans les statiques
        p = None
        try:
            p = api_client.api_get(f"products/{pid}/", token)
        except RequestException:
            pass
        if p is None:
            # Recherche dans les produits statiques
            p = next((med for med in STATIC_MEDICATIONS if str(med["id"]) == pid), None)
            if p is None:
                continue
            # Le prix est déjà en dinars dans les statiques
            price_dzd = p.get("price_dzd", 0)
            p = p.copy()  # pour éviter de modifier la liste originale
        else:
            price_eur = float(p.get("price", 0))
            price_dzd = to_dzd(price_eur)
            p["price_dzd"] = price_dzd
        line_total_dzd = price_dzd * qty
        total_dzd += line_total_dzd
        lines.append({
            "product": p,
            "quantity": qty,
            "line_total_dzd": line_total_dzd,
        })
    return render(request, "shop/cart.html", {"lines": lines, "cart_total_dzd": total_dzd})

def checkout(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect("cart")
    payload_lines = [{"product_id": int(k), "quantity": int(v)} for k, v in cart.items()]
    try:
        api_client.api_post("orders/", _token(request), {"lines": payload_lines})
    except HTTPError as e:
        messages.error(request, str(e))
        return redirect("cart")
    except RequestException:
        messages.error(request, "Impossible de finaliser la commande.")
        return redirect("cart")
    request.session["cart"] = {}
    messages.success(request, "Commande enregistrée. Une notification a été envoyée.")
    return redirect("orders")

def orders(request):
    redir = _require_auth(request)
    if redir:
        return redir
    try:
        data = api_client.api_get("orders/", _token(request))
    except RequestException:
        messages.error(request, "Historique indisponible.")
        return render(request, "shop/orders.html", {"results": []})
    results = data.get("results", data) if isinstance(data, dict) else data
    if not isinstance(results, list):
        results = []
    for order in results:
        order["total_dzd"] = to_dzd(order.get("total", 0))
        # Si l'API renvoie un sous-total, on peut aussi le convertir
        order["subtotal_dzd"] = to_dzd(order.get("subtotal", 0))
        for line in order.get("lines", []):
            line["unit_price_dzd"] = to_dzd(line.get("unit_price", 0))
    return render(request, "shop/orders.html", {"results": results})