from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("connexion/", views.login_view, name="login"),
    path("deconnexion/", views.logout_view, name="logout"),
    path("inscription/", views.signup_view, name="signup"),
    path("catalogue/", views.catalog, name="catalog"),
    path("panier/", views.cart_view, name="cart"),
    path("panier/ajouter/", views.cart_add, name="cart_add"),
    path("panier/modifier/<int:product_id>/", views.cart_update, name="cart_update"),
    path("panier/retirer/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("commander/", views.checkout, name="checkout"),
    path("commandes/", views.orders, name="orders"),
]