import base64
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from requests import HTTPError, RequestException

from . import api_client
from .presentation import build_catalog_metrics, decorate_product, decorate_products


def health_check(request):
    return JsonResponse({"status": "ok", "service": "web-ui"})


def _token(request):
    return request.session.get("access")


def _is_admin(request):
    token = _token(request)
    if not token:
        return False
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        return data.get("role") == "ADMIN"
    except Exception:
        return False


def _require_admin(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    if not _is_admin(request):
        messages.error(request, "Acces reserve aux administrateurs.")
        return redirect("home")
    return None


def _require_auth(request):
    if not _token(request):
        return redirect(f"{reverse('login')}?next={request.path}")
    return None


def _api_results(data):
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    if isinstance(data, list):
        return data
    return []


def _api_count(data):
    if isinstance(data, dict) and "count" in data:
        return data["count"]
    return len(_api_results(data))


def _estimated_discount_percent(subtotal: float) -> int:
    if subtotal >= 1500:
        return 5
    if subtotal >= 1000:
        return 4
    if subtotal >= 500:
        return 3
    if subtotal >= 250:
        return 2
    return 0


def set_language(request):
    desired = request.GET.get("lang", "fr")
    if desired not in ("fr", "ar"):
        desired = "fr"
    request.session["lang"] = desired
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or reverse("home")
    return redirect(next_url)


def home(request):
    search_query = request.GET.get("q", "").strip()
    if search_query:
        return redirect(f"{reverse('catalog')}?q={search_query}")

    featured_products = []
    categories = []
    catalog_stats = {
        "total_products": 0,
        "featured_count": 0,
        "category_count": 0,
        "low_stock_count": 0,
        "out_of_stock_count": 0,
        "expiring_count": 0,
    }

    try:
        featured_data = api_client.api_get(
            "products/",
            _token(request),
            params={"featured": "true", "ordering": "-rating"},
        )
        featured_products = decorate_products(_api_results(featured_data)[:8])
        catalog_stats["featured_count"] = _api_count(featured_data)
    except RequestException:
        featured_products = []

    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = _api_results(categories_data)
        catalog_stats["category_count"] = len(categories)
        catalog_stats["total_products"] = sum(int(category.get("product_count") or 0) for category in categories)
    except RequestException:
        categories = []

    if featured_products:
        metrics = build_catalog_metrics(featured_products, categories)
        catalog_stats["low_stock_count"] = metrics["low_stock_count"]
        catalog_stats["out_of_stock_count"] = metrics["out_of_stock_count"]
        catalog_stats["expiring_count"] = metrics["expiring_count"]

    return render(
        request,
        "shop/home.html",
        {
            "authenticated": bool(_token(request)),
            "featured_products": featured_products,
            "home_categories": categories[:6],
            "catalog_stats": catalog_stats,
            "search_query": search_query,
        },
    )


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
            messages.error(request, "Impossible de joindre le service d'authentification.")
            return render(request, "shop/login.html")
        request.session["access"] = data.get("access")
        request.session["refresh"] = data.get("refresh")
        messages.success(request, "Connexion reussie.")
        next_url = request.GET.get("next") or (reverse("admin_dashboard") if _is_admin(request) else reverse("catalog"))
        return redirect(next_url)
    return render(request, "shop/login.html")


def logout_view(request):
    request.session.flush()
    messages.info(request, "Vous etes deconnecte.")
    return redirect("home")


def signup_view(request):
    if _token(request):
        return redirect("catalog")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("full_name", "").strip()

        if not email or not password:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, "shop/signup.html")
        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "shop/signup.html")
        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caracteres.")
            return render(request, "shop/signup.html")

        try:
            api_client.auth_register(email=email, password=password, first_name=first_name, role="PRO")
        except HTTPError as error:
            try:
                messages.error(request, str(error.response.json()))
            except Exception:
                messages.error(request, "Erreur lors de l'enregistrement.")
            return render(request, "shop/signup.html")
        except RequestException:
            messages.error(request, "Impossible de contacter le service d'authentification.")
            return render(request, "shop/signup.html")

        messages.success(request, "Inscription reussie. Vous pouvez maintenant vous connecter.")
        return redirect("login")

    return render(request, "shop/signup.html")


def catalog(request):
    params = {}
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    min_stock = request.GET.get("min_stock", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    availability = request.GET.get("availability", "").strip()
    ordering = request.GET.get("ordering", "").strip()
    featured = request.GET.get("featured", "").strip()
    selected_category_id = None

    if q:
        params["search"] = q
    if min_price:
        params["min_price"] = min_price
    if max_price:
        params["max_price"] = max_price
    if availability:
        params["availability"] = availability
    if ordering:
        params["ordering"] = ordering
    if featured:
        params["featured"] = featured

    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = _api_results(categories_data)
    except RequestException:
        categories = []

    if category:
        if category.isdigit():
            params["category"] = category
            selected_category_id = int(category)
        else:
            category_slug = category.lower()
            if category_slug == "test":
                category_slug = "tests"
            params["category__slug"] = category_slug
            for cat in categories:
                if str(cat.get("slug", "")).lower() == category_slug:
                    selected_category_id = cat.get("id")
                    break
                if str(cat.get("name", "")).lower() == category_slug:
                    selected_category_id = cat.get("id")
                    params["category__slug"] = cat.get("slug")
                    break

    try:
        data = api_client.api_get("products/", _token(request), params=params or None)
    except RequestException:
        messages.error(request, "Catalogue indisponible.")
        return render(request, "shop/catalog.html", {"results": [], "categories": categories})

    results = _api_results(data)
    if min_stock:
        try:
            minimum = int(min_stock)
            results = [product for product in results if int(product.get("stock", 0)) >= minimum]
        except (TypeError, ValueError):
            pass

    results = decorate_products(results)
    catalog_metrics = build_catalog_metrics(results, categories)

    return render(
        request,
        "shop/catalog.html",
        {
            "results": results,
            "categories": categories,
            "selected_category_id": selected_category_id,
            "catalog_metrics": catalog_metrics,
            "result_count": _api_count(data),
            "availability": availability,
            "ordering": ordering,
            "featured_only": featured,
        },
    )


def _get_cart(request) -> dict[str, int]:
    cart = request.session.get("cart") or {}
    out = {}
    for key, value in cart.items():
        try:
            out[str(int(key))] = max(1, int(value))
        except (TypeError, ValueError):
            continue
    request.session["cart"] = out
    return out


def cart_add(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    key = str(product_id)
    try:
        product = api_client.api_get(f"products/{product_id}/", _token(request))
        min_quantity = max(1, int(product.get("min_order_quantity") or 1))
    except (RequestException, TypeError, ValueError):
        min_quantity = 1
    cart[key] = cart.get(key, 0) + min_quantity
    request.session["cart"] = cart
    messages.success(request, "Produit ajoute au panier.")
    return redirect("cart")


def cart_remove(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart")


def cart_update(request, product_id: int):
    redir = _require_auth(request)
    if redir:
        return redir
    if request.method == "POST":
        cart = _get_cart(request)
        quantity = request.POST.get("quantity", "0").strip()
        try:
            qty = int(quantity)
            product = api_client.api_get(f"products/{product_id}/", _token(request))
            minimum = max(1, int(product.get("min_order_quantity") or 1))
            if qty > 0:
                cart[str(product_id)] = max(minimum, qty)
                messages.success(request, "Quantite mise a jour.")
            else:
                cart.pop(str(product_id), None)
                messages.info(request, "Produit retire du panier.")
        except (ValueError, TypeError, RequestException):
            messages.error(request, "Quantite invalide.")
        request.session["cart"] = cart
    return redirect("cart")


def cart_view(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    lines = []
    total = 0.0
    token = _token(request)
    for pid, qty in cart.items():
        try:
            product = decorate_product(api_client.api_get(f"products/{pid}/", token))
        except RequestException:
            continue
        price = float(product.get("price", 0))
        line_total = price * qty
        total += line_total
        lines.append({"product": product, "quantity": qty, "line_total": line_total})
    discount_percent = _estimated_discount_percent(total)
    discount_total = round(total * (100 - discount_percent) / 100, 2) if discount_percent else round(total, 2)
    return render(
        request,
        "shop/cart.html",
        {
            "lines": lines,
            "cart_total": round(total, 2),
            "discount_percent": discount_percent,
            "discount_total": discount_total,
        },
    )


def checkout(request):
    redir = _require_auth(request)
    if redir:
        return redir
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect("cart")

    token = _token(request)
    cart_items = []
    cart_total = 0.0
    for pid, qty in cart.items():
        try:
            product = decorate_product(api_client.api_get(f"products/{pid}/", token))
        except RequestException:
            continue
        line_total = float(product.get("price", 0)) * qty
        cart_total += line_total
        cart_items.append({"product": product, "quantity": qty, "total_price": round(line_total, 2)})

    discount_percent = _estimated_discount_percent(cart_total)
    discount_total = round(cart_total * (100 - discount_percent) / 100, 2) if discount_percent else round(cart_total, 2)

    if request.method != "POST":
        return render(
            request,
            "shop/checkout.html",
            {
                "cart_items": cart_items,
                "cart_total": round(cart_total, 2),
                "discount_percent": discount_percent,
                "discount_total": discount_total,
            },
        )

    payload = {
        "lines": [{"product_id": int(key), "quantity": int(value)} for key, value in cart.items()],
        "phone": request.POST.get("phone", ""),
        "email": request.POST.get("email", ""),
        "city": request.POST.get("city", ""),
        "commune": request.POST.get("commune", ""),
        "detailed_address": request.POST.get("detailed_address", ""),
        "postal_code": request.POST.get("postal_code", ""),
        "delivery_method": request.POST.get("delivery_method", "domicile"),
    }
    try:
        api_client.api_post("orders/", token, payload)
    except HTTPError as error:
        messages.error(request, str(error))
        return redirect("checkout")
    except RequestException:
        messages.error(request, "Impossible de finaliser la commande.")
        return redirect("checkout")

    request.session["cart"] = {}
    messages.success(request, "Commande enregistree. Le circuit logistique a bien ete notifie.")
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
    results = _api_results(data)
    for order in results:
        status = order.get("status")
        if status in {"CONFIRMED", "SHIPPED", "DELIVERED"}:
            order["status_class"] = "badge-ok"
        elif status == "PENDING":
            order["status_class"] = "badge-low"
        else:
            order["status_class"] = "badge-out"
    return render(request, "shop/orders.html", {"results": results})


def admin_dashboard(request):
    redir = _require_admin(request)
    if redir:
        return redir
    return render(request, "shop/admin/dashboard.html")


def admin_products_list(request):
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        data = api_client.api_get("products/", _token(request))
        products = _api_results(data)
    except RequestException:
        messages.error(request, "Impossible de charger les produits.")
        products = []

    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = _api_results(categories_data)
    except RequestException:
        categories = []

    return render(request, "shop/admin/products_list.html", {"products": products, "categories": categories})


def admin_product_create(request):
    redir = _require_admin(request)
    if redir:
        return redir

    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = _api_results(categories_data)
    except RequestException:
        categories = []

    if request.method == "POST":
        payload = {
            "name": request.POST.get("name", "").strip(),
            "slug": request.POST.get("slug", "").strip().lower().replace(" ", "-"),
            "summary": request.POST.get("summary", "").strip(),
            "price": float(request.POST.get("price", 0)),
            "stock": int(request.POST.get("stock", 0)),
            "sku": request.POST.get("sku", "").strip().upper(),
            "category": int(request.POST.get("category", 0)),
        }
        try:
            api_client.api_post("products/", _token(request), payload)
            messages.success(request, "Produit cree avec succes.")
            return redirect("admin_products_list")
        except HTTPError as error:
            messages.error(request, f"Erreur: {error}")
        except RequestException:
            messages.error(request, "Erreur de communication avec le serveur.")

    return render(request, "shop/admin/product_form.html", {"categories": categories})


def admin_product_edit(request, product_id: int):
    redir = _require_admin(request)
    if redir:
        return redir

    try:
        product = api_client.api_get(f"products/{product_id}/", _token(request))
    except RequestException:
        messages.error(request, "Produit non trouve.")
        return redirect("admin_products_list")

    try:
        categories_data = api_client.api_get("categories/", _token(request))
        categories = _api_results(categories_data)
    except RequestException:
        categories = []

    if request.method == "POST":
        payload = {
            "name": request.POST.get("name", product.get("name", "")).strip(),
            "slug": request.POST.get("slug", product.get("slug", "")).strip().lower().replace(" ", "-"),
            "summary": request.POST.get("summary", product.get("summary", "")).strip(),
            "price": float(request.POST.get("price", product.get("price", 0))),
            "stock": int(request.POST.get("stock", product.get("stock", 0))),
            "sku": request.POST.get("sku", product.get("sku", "")).strip().upper(),
            "category": int(request.POST.get("category", product.get("category", 0))),
        }
        try:
            api_client.api_patch(f"products/{product_id}/", _token(request), payload)
            messages.success(request, "Produit mis a jour.")
            return redirect("admin_products_list")
        except HTTPError:
            messages.error(request, "Erreur lors de la mise a jour.")
        except RequestException:
            messages.error(request, "Erreur de communication.")

    return render(request, "shop/admin/product_form.html", {"product": product, "categories": categories})


def admin_product_delete(request, product_id: int):
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        api_client.api_delete(f"products/{product_id}/", _token(request))
        messages.success(request, "Produit supprime.")
    except RequestException:
        messages.error(request, "Erreur lors de la suppression.")
    return redirect("admin_products_list")


def admin_orders_list(request):
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        data = api_client.api_get("orders/", _token(request))
        orders_list = _api_results(data)
    except RequestException:
        messages.error(request, "Impossible de charger les commandes.")
        orders_list = []
    return render(request, "shop/admin/orders_list.html", {"orders": orders_list})


def admin_order_detail(request, order_id: int):
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        order = api_client.api_get(f"orders/{order_id}/", _token(request))
    except RequestException:
        messages.error(request, "Commande non trouvee.")
        return redirect("admin_orders_list")

    if "lines" in order and isinstance(order.get("lines"), list):
        for line in order["lines"]:
            line["line_total"] = float(line.get("unit_price", 0)) * int(line.get("quantity", 1))

    if request.method == "POST":
        status = request.POST.get("status", "").strip()
        if status in ["PENDING", "CONFIRMED", "SHIPPED", "CANCELLED", "DELIVERED"]:
            try:
                api_client.api_patch(f"orders/{order_id}/", _token(request), {"status": status})
                messages.success(request, "Statut mis a jour.")
                return redirect("admin_order_detail", order_id=order_id)
            except RequestException:
                messages.error(request, "Erreur lors de la mise a jour du statut.")

    return render(request, "shop/admin/order_detail.html", {"order": order})


def admin_statistics(request):
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        orders_data = api_client.api_get("orders/", _token(request))
        orders = _api_results(orders_data)
        products_data = api_client.api_get("products/", _token(request))
        products_count = _api_count(products_data)
        total_revenue = sum(float(order.get("total", 0)) for order in orders if order.get("status") != "CANCELLED")
        pending_orders = len([order for order in orders if order.get("status") == "PENDING"])
        stats = {
            "total_orders": len(orders),
            "total_revenue": total_revenue,
            "products_count": products_count,
            "pending_orders": pending_orders,
        }
    except Exception as error:
        messages.error(request, f"Erreur lors du chargement des statistiques: {error}")
        stats = {"total_orders": 0, "total_revenue": 0, "products_count": 0, "pending_orders": 0}
    return render(request, "shop/admin/statistics.html", {"stats": stats})


def admin_users_list(request):
    redir = _require_admin(request)
    if redir:
        return redir
    try:
        data = api_client.auth_get("users/", _token(request))
        users = _api_results(data)
    except Exception as error:
        messages.error(request, f"Impossible de charger la liste des utilisateurs: {error}")
        users = []
    return render(request, "shop/admin/users_list.html", {"users": users})


@csrf_exempt
def product_like(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method != "POST":
        return json_response({"error": "Method not allowed"}, status=405)
    try:
        data = api_client.api_post(f"products/{product_id}/like/", _token(request))
        return json_response(data)
    except RequestException as error:
        return json_response({"error": str(error)}, status=500)


@csrf_exempt
def product_recommend(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method != "POST":
        return json_response({"error": "Method not allowed"}, status=405)
    try:
        data = api_client.api_post(f"products/{product_id}/recommend/", _token(request))
        return json_response(data)
    except RequestException as error:
        return json_response({"error": str(error)}, status=500)


@csrf_exempt
def product_rate(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            data = api_client.api_post(f"products/{product_id}/rate/", _token(request), body)
            return json_response(data)
        except RequestException as error:
            return json_response({"error": str(error)}, status=500)
    return json_response({"error": "Method not allowed"}, status=405)


@csrf_exempt
def product_unrate(request, product_id):
    if not _token(request):
        return json_response({"error": "Unauthorized"}, status=401)
    if request.method != "POST":
        return json_response({"error": "Method not allowed"}, status=405)
    try:
        data = api_client.api_post(f"products/{product_id}/unrate/", _token(request))
        return json_response(data)
    except RequestException as error:
        return json_response({"error": str(error)}, status=500)


def json_response(data, status=200):
    return JsonResponse(data, status=status)
