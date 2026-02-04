from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los usuarios acceder a sus propios datos.
    """
    message = "No tienes permiso para acceder a este recurso."
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica que el objeto pertenezca al usuario autenticado.
        Funciona con modelos que tienen un campo 'user'.
        """
        # Para Profile y Mascota (OneToOne con User)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Para el modelo User mismo
        if obj.__class__.__name__ == 'User':
            return obj == request.user
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos pero escritura solo al propietario.
    """
    def has_object_permission(self, request, view, obj):
        # Permiso de lectura (GET, HEAD, OPTIONS) para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permiso de escritura solo para el propietario
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
