from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import User
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer, \
    RequestResetPasswordEmailSerializer, SetNewPasswordSerializer
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
        data = {'request': request, 'data': request.data}
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestResetPasswordEmail(generics.GenericAPIView):
    serializer_class = RequestResetPasswordEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # send email
            current_site = get_current_site(request=request).domain
            relative_link = reverse_lazy('password-reset-confirm',
                                         kwargs={'uidb64': uidb64,
                                                 'token': token})
            absurl = f'http://{current_site}{relative_link}'

            email_body = f'Hello \nUse link below to reset your password.\n{absurl}'
            data = {
                'to_email': user.email,
                'email_body': email_body,
                'email_subject': 'Reset your password',
            }

            Util.send_email(data)

        return Response({'success': 'Reset link sent to your email'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_401_UNAUTHORIZED)

            return Response(data={'success': True,
                                  'message': 'Credential valid',
                                  'uidb64': uidb64,
                                  'token': token},
                            status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid, please request a new one'},
                            status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
