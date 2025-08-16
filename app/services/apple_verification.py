import logging
import jwt
import httpx
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cachetools import TTLCache
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.configs import settings


class AppleVerificationService:
    """Service for verifying Apple Sign In tokens"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Cache for Apple public keys (TTL cache with 1 hour expiration)
        self._keys_cache = TTLCache(maxsize=10, ttl=settings.apple_signin.TOKEN_CACHE_TTL)
        self._http_client = httpx.AsyncClient(timeout=30.0)
    
    async def verify_apple_token(
        self, 
        identity_token: str, 
        apple_id: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify Apple identity token and extract user info.
        
        Args:
            identity_token: JWT token from Apple Sign In
            apple_id: Apple user identifier
            name: User's name from Apple (optional, only provided on first sign in)
            
        Returns:
            Dict with verification result and user data
        """
        self.logger.info(f"Verifying Apple token for user: {apple_id}")
        self.logger.debug(f"Token length: {len(identity_token) if identity_token else 0}")
        self.logger.debug(f"Token preview: {identity_token[:50] if identity_token else 'None'}...")
        
        try:
            # Step 1: Validate token structure
            if not self._validate_token_structure(identity_token):
                self.logger.error(f"Invalid JWT token structure for user: {apple_id}")
                return {
                    "valid": False,
                    "error": "Invalid JWT token structure",
                    "apple_id": apple_id,
                    "name": name,
                    "verified": False
                }
            
            # Step 2: Get Apple public keys
            apple_keys = await self.get_apple_public_keys()
            if not apple_keys.get("keys"):
                self.logger.error(f"Failed to fetch Apple public keys: {apple_keys.get('error', 'Unknown error')}")
                return {
                    "valid": False,
                    "error": "Failed to fetch Apple public keys",
                    "apple_id": apple_id,
                    "name": name,
                    "verified": False
                }
            
            # Step 3: Decode and verify JWT token
            self.logger.debug(f"Attempting to verify JWT signature with {len(apple_keys['keys'])} keys")
            token_claims = await self._verify_jwt_signature(identity_token, apple_keys["keys"])
            if not token_claims:
                self.logger.error(f"JWT signature verification failed for user: {apple_id}")
                return {
                    "valid": False,
                    "error": "Invalid JWT signature or expired token",
                    "apple_id": apple_id,
                    "name": name,
                    "verified": False
                }
            
            # Step 4: Validate claims
            self.logger.debug(f"Validating token claims: {list(token_claims.keys())}")
            validation_result = self._validate_token_claims(token_claims, apple_id)
            if not validation_result["valid"]:
                self.logger.error(f"Token claims validation failed: {validation_result['error']}")
                return {
                    "valid": False,
                    "error": validation_result["error"],
                    "apple_id": apple_id,
                    "name": name,
                    "verified": False
                }
            
            # Step 5: Extract user information
            extracted_name = name or token_claims.get("given_name", "Apple User")
            extracted_email = token_claims.get("email")
            
            self.logger.info(f"Apple token verified successfully for user: {apple_id}")
            
            return {
                "valid": True,
                "apple_id": token_claims["sub"],  # Use Apple's sub claim
                "name": extracted_name,
                "email": extracted_email,
                "verified": True,
                "error": None,
                "token_claims": token_claims  # Include for debugging
            }
            
        except Exception as e:
            self.logger.error(f"Error verifying Apple token: {str(e)}")
            return {
                "valid": False,
                "error": f"Token verification failed: {str(e)}",
                "apple_id": apple_id,
                "name": name,
                "verified": False
            }
    
    async def get_apple_public_keys(self) -> Dict[str, Any]:
        """
        Fetch Apple's public keys for token verification with caching.
        
        Returns:
            Dict containing Apple's current public keys
        """
        # Check cache first
        cache_key = "apple_public_keys"
        if cache_key in self._keys_cache:
            self.logger.debug("Using cached Apple public keys")
            return self._keys_cache[cache_key]
        
        self.logger.info("Fetching Apple public keys from server")
        
        try:
            response = await self._http_client.get(settings.apple_signin.APPLE_KEYS_URL)
            response.raise_for_status()
            
            keys_data = response.json()
            
            # Validate keys structure
            if "keys" not in keys_data or not isinstance(keys_data["keys"], list):
                raise ValueError("Invalid keys format from Apple")
            
            result = {
                "keys": keys_data["keys"],
                "fetched_at": datetime.utcnow().isoformat(),
                "cache_duration": settings.apple_signin.TOKEN_CACHE_TTL
            }
            
            # Cache the result
            self._keys_cache[cache_key] = result
            
            self.logger.info(f"Fetched {len(keys_data['keys'])} Apple public keys")
            return result
            
        except httpx.RequestError as e:
            self.logger.error(f"Network error fetching Apple keys: {e}")
            return {"keys": [], "error": f"Network error: {str(e)}"}
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching Apple keys: {e}")
            return {"keys": [], "error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            self.logger.error(f"Unexpected error fetching Apple keys: {e}")
            return {"keys": [], "error": f"Unexpected error: {str(e)}"}
    
    def _validate_token_structure(self, token: str) -> bool:
        """
        Validate basic JWT token structure.
        
        Args:
            token: JWT token string
            
        Returns:
            bool: True if token has valid JWT structure
        """
        if not token or not isinstance(token, str):
            return False
        
        # JWT should have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Each part should be non-empty
        for part in parts:
            if not part:
                return False
        
        return True
    
    async def _verify_jwt_signature(self, token: str, apple_keys: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Verify JWT signature using Apple's public keys and extract claims.
        
        Args:
            token: JWT token string
            apple_keys: List of Apple public keys
            
        Returns:
            Dict with token claims or None if invalid
        """
        try:
            # Get token header to find the key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            alg = unverified_header.get("alg")
            
            self.logger.debug(f"Token header: kid={kid}, alg={alg}")
            
            if not kid:
                self.logger.error("Token header missing 'kid' claim")
                return None
            
            # Find the matching key
            matching_key = None
            available_kids = [key.get("kid") for key in apple_keys]
            self.logger.debug(f"Available key IDs: {available_kids}")
            
            for key in apple_keys:
                if key.get("kid") == kid:
                    matching_key = key
                    break
            
            if not matching_key:
                self.logger.error(f"No matching key found for kid: {kid}, available kids: {available_kids}")
                return None
            
            # Convert JWK to PEM format for verification
            public_key = self._jwk_to_pem(matching_key)
            if not public_key:
                self.logger.error("Failed to convert JWK to PEM")
                return None
            
            # Verify and decode the token
            self.logger.debug(f"Verifying token with audience: {settings.apple_signin.BUNDLE_ID}, issuer: {settings.apple_signin.APPLE_ISSUER}")
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=[alg],
                audience=settings.apple_signin.BUNDLE_ID,
                issuer=settings.apple_signin.APPLE_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True
                }
            )
            
            self.logger.debug(f"Successfully decoded token with claims: {list(decoded_token.keys())}")
            return decoded_token
            
        except jwt.ExpiredSignatureError as e:
            self.logger.error(f"Token has expired: {e}")
            return None
        except jwt.InvalidAudienceError as e:
            self.logger.error(f"Invalid audience in token. Expected: {settings.apple_signin.BUNDLE_ID}, Error: {e}")
            return None
        except jwt.InvalidIssuerError as e:
            self.logger.error(f"Invalid issuer in token. Expected: {settings.apple_signin.APPLE_ISSUER}, Error: {e}")
            return None
        except jwt.InvalidSignatureError as e:
            self.logger.error(f"Invalid token signature: {e}")
            return None
        except jwt.DecodeError as e:
            self.logger.error(f"JWT decode error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error verifying JWT signature: {e}")
            return None
    
    def _jwk_to_pem(self, jwk: Dict[str, Any]) -> Optional[str]:
        """
        Convert JSON Web Key to PEM format.
        
        Args:
            jwk: JSON Web Key dictionary
            
        Returns:
            PEM formatted public key string or None if conversion fails
        """
        try:
            from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
            from cryptography.hazmat.primitives import serialization
            import base64
            
            # Decode the modulus and exponent from the JWK
            n = int.from_bytes(base64.urlsafe_b64decode(jwk['n'] + '=='), 'big')
            e = int.from_bytes(base64.urlsafe_b64decode(jwk['e'] + '=='), 'big')
            
            # Create RSA public key
            public_numbers = RSAPublicNumbers(e, n)
            public_key = public_numbers.public_key()
            
            # Convert to PEM format
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return pem.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error converting JWK to PEM: {e}")
            return None
    
    def _validate_token_claims(self, claims: Dict[str, Any], expected_apple_id: str) -> Dict[str, Any]:
        """
        Validate token claims against expected values.
        
        Args:
            claims: Decoded JWT claims
            expected_apple_id: Expected Apple user ID
            
        Returns:
            Dict with validation result
        """
        try:
            # Check required claims
            required_claims = ["sub", "aud", "iss", "exp", "iat"]
            for claim in required_claims:
                if claim not in claims:
                    return {"valid": False, "error": f"Missing required claim: {claim}"}
            
            # Validate issuer
            if claims["iss"] != settings.apple_signin.APPLE_ISSUER:
                return {"valid": False, "error": f"Invalid issuer: {claims['iss']}"}
            
            # Validate audience (should be our bundle ID)
            if claims["aud"] != settings.apple_signin.BUNDLE_ID:
                return {"valid": False, "error": f"Invalid audience: {claims['aud']}"}
            
            # Validate subject (Apple user ID) if provided
            if expected_apple_id and claims["sub"] != expected_apple_id:
                self.logger.warning(f"Apple ID mismatch: expected {expected_apple_id}, got {claims['sub']}")
                # Don't fail here, use the token's sub instead
            
            # Check token is not expired (JWT library already validates this, but double-check)
            # Note: Apple tokens use local time, not UTC
            current_time = datetime.now().timestamp()
            self.logger.debug(f"Token times - iat: {claims['iat']}, exp: {claims['exp']}, current: {current_time}")
            
            if claims["exp"] < current_time:
                return {"valid": False, "error": "Token has expired"}
            
            # Check token is not used before issued time (with 60 second tolerance for clock skew)
            tolerance_seconds = 60
            if claims["iat"] > (current_time + tolerance_seconds):
                self.logger.error(f"Token iat={claims['iat']}, current_time={current_time}, diff={claims['iat'] - current_time} seconds")
                return {"valid": False, "error": "Token used before issued time"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Claims validation error: {str(e)}"}


# Create service instance
apple_verification_service = AppleVerificationService()
