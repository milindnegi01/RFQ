from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))
        return self.get_response(request)

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            print(f"User already authenticated: {user.username}, role: {user.role}")
            return user

        jwt_authentication = JWTAuthentication()
        
        # First try to get token from Authorization header
        auth_header = jwt_authentication.get_header(request)
        if auth_header:
            try:
                user_auth_tuple = jwt_authentication.authenticate(request)
                if user_auth_tuple is not None:
                    user = user_auth_tuple[0]
                    print(f"User authenticated from header: {user.username}, role: {user.role}")
                    return user
            except Exception as e:
                print(f"JWT Authentication error: {str(e)}")
                return user

        # Then try to get token from cookies
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if access_token:
            try:
                # Set the Authorization header with the cookie token
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                user_auth_tuple = jwt_authentication.authenticate(request)
                if user_auth_tuple is not None:
                    user = user_auth_tuple[0]
                    print(f"User authenticated from cookie: {user.username}, role: {user.role}")
                    return user
            except Exception as e:
                print(f"Cookie JWT Authentication error: {str(e)}")
                return user

        print("No user authenticated")
        return user