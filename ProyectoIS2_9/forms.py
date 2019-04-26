from django.contrib.auth.forms import AuthenticationForm
from django.forms import ValidationError

class NuestroAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.error_messages['no_su_ni_staff'] = (
            'No se permite login a superusuarios ni usuarios staff.'
        )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_superuser or user.is_staff:
            raise ValidationError(
                self.error_messages['no_su_ni_staff'],
                code='no_su_ni_staff'
            )
