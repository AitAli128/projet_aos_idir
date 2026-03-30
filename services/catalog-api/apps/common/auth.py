from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings


class CatalogUser:
    """Utilisateur dérivé du JWT (pas de ligne User dans cette base)."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, token):
        try:
            uid = token[api_settings.USER_ID_CLAIM]
        except KeyError as e:
            raise InvalidToken("Jeton sans identifiant utilisateur") from e
        self.id = int(uid)
        self.pk = self.id
        self.role = token.get("role", "PRO")
        self.email = token.get("email", "")

    @property
    def is_staff(self):
        return self.role == "ADMIN"

    @property
    def is_superuser(self):
        return self.role == "ADMIN"


class CatalogJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        return CatalogUser(validated_token)
