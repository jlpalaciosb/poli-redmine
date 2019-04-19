from django.contrib.auth.mixins import PermissionRequiredMixin

class PermissionRequiredAndNotSuperUserMixin(PermissionRequiredMixin):
    """
    Mixin a utilizar para prohibir el acceso a un usuario particular que sea superuser o staff de django admin
    """
    def has_permission(self):
        """
        Se sobreescibe para prohibir acceso para aquellos usuarios que son super_user o staff
        :return:
        """
        user = self.get_object()
        if(user.is_staff or user.is_superuser):
            return False
        return super().has_permission()