from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsQuizOwner(BasePermission):
    message = 'Zugriff verweigert – Quiz gehört nicht dem Benutzer.'

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
