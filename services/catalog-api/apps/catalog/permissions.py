from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(getattr(request.user, "is_staff", False))


class IsAdminOrPharmacyOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        role = request.auth.get("role") if request.auth else getattr(request.user, "role", None)
        return bool(getattr(request.user, "is_staff", False)) or role in ["ADMIN", "PHARMACY"]

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        role = request.auth.get("role") if request.auth else getattr(request.user, "role", None)
        if bool(getattr(request.user, "is_staff", False)) or role == "ADMIN":
            return True
        return obj.auth_user_id == request.user.id


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_staff", False):
            return True
        return obj.auth_user_id == request.user.id
