from cryptography.fernet import Fernet
import jwt, os, dotenv
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class ForgetPasswordThrottle(AnonRateThrottle):
    rate = '2/min'

class LoginThrottle(UserRateThrottle):
    rate = '5/min'
    
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings

class DevelopmentSecurityHeadersMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not settings.DEBUG and not request.is_secure():
            return JsonResponse({'error': 'HTTPS is required for secure communication.'}, status=403)

    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'

        if not settings.DEBUG:
            response['Content-Security-Policy'] = "default-src 'self';"

        return response


dotenv.load_dotenv(os.path.join(settings.BASE_DIR, 'config', '.env'))

key = Fernet.generate_key()
cipher_suite = Fernet(key)
JWT_SECRET = os.getenv("SECRET_KEY")



def create_token(payload):
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    encrypted_token = cipher_suite.encrypt(token.encode()).decode()
    return encrypted_token


def decrypt_token(enc_token):
    try:
        dec_token = cipher_suite.decrypt(enc_token.encode()).decode()
        payload = jwt.decode(dec_token, JWT_SECRET, algorithms=['HS256'])
        return {'payload': payload, 'status': True}
    except:
        return {'status': False}