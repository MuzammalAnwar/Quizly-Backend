from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    If Authorization header is missing, try to read JWT from 'access_token' cookie.
    """
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get("access_token")
            if raw_token:
                validated = self.get_validated_token(raw_token)
                return self.get_user(validated), validated
        return super().authenticate(request)
