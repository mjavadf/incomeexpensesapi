from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import User
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer
from .renderers import UserRenderer
from .utils import Util
import jwt


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink = reverse_lazy('email-verify')
        absurl = f'http://{current_site}{relativeLink}?token={str(token)}'

        email_body = f'Hello dear {user.username}, Use link below to verify your account\n{absurl}'
        data = {
            'to_email': user.email,
            'email_body': email_body,
            'email_subject': 'Verify Your Account',
        }

        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token',
        in_=openapi.IN_QUERY,
        description='Description',
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'messages': 'Account successfully verified'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'messages': 'Activation link is expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError:
            return Response({'messages': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return  Response(serializer.data, status=status.HTTP_200_OK)
