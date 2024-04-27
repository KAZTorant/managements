from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions

User = get_user_model()


class PINAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        pin = request.headers.get('X-PIN')
        if not pin:
            return None

        try:
            user = User.objects.get(username=pin)
            if user.is_active:
                return (user, None)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return None
