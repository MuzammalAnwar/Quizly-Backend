from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            serializer.save()
            data = {
                'detail': 'User created successfully!'
            }
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieObtainPairView(TokenObtainPairView):
    def set_auth_cookies(self, response, access, refresh):
        for name, value in (('access_token', access), ('refresh_token', refresh)):
            response.set_cookie(
                key=name,
                value=str(value),
                httponly=True,
                secure=True,
                samesite='Lax',
                path='/',
            )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        access, refresh = serializer.validated_data.get(
            'access'), serializer.validated_data.get('refresh')

        res = Response({
            'detail': 'Login successful!',
            'user': {'id': user.id, 'username': user.username, 'email': user.email},
        }, status=status.HTTP_200_OK)

        self.set_auth_cookies(res, access, refresh)
        return res


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh Token not found!'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({'detail': 'Refresh Token is invalid!'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get('access')

        resp = Response(
            {'detail': 'Token refreshed', 'access': access_token},
            status=status.HTTP_200_OK,
        )
        resp.set_cookie(
            key='access_token',
            value=str(access_token),
            httponly=True,
            secure=True,
            samesite='Lax',
            path='/',
        )
        return resp


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response(
            {
                'detail': 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie('access_token', path='/', samesite='Lax')
        response.delete_cookie('refresh_token', path='/', samesite='Lax')

        return response
