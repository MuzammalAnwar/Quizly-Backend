from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
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
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.get('refresh')
        access = response.data.get('access')

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        
        return Response(
            {
                
            }
        )
