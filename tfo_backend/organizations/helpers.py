import jwt
from datetime import datetime
from django.conf import settings


class OrganizationToken:
    def __init__(self):
        self.settings = settings.ORGANIZATION_JWT_SETTINGS

    def encode(self, payload):
        """
        Encode a JWT token for organization staff.
        Adds an expiration time (`exp`) to the payload.
        """
        payload['exp'] = datetime.utcnow() + self.settings['ACCESS_TOKEN_LIFETIME']
        return jwt.encode(payload, self.settings['SIGNING_KEY'], algorithm=self.settings['ALGORITHM'])

    def decode(self, token):
        """
        Decode a JWT token for organization staff.
        Validates the token using the same `SIGNING_KEY`.
        """
        try:
            print("ffffffffff")
            return jwt.decode(
                token,
                self.settings['SIGNING_KEY'],  # Symmetric key for validation
                algorithms=[self.settings['ALGORITHM']]
            )
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")