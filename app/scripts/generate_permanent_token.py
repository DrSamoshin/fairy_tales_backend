#!/usr/bin/env python3
"""
Interactive script to generate permanent JWT tokens without expiration date.
Usage: python generate_permanent_token.py
The script will prompt for User ID input.
"""

import sys
import jwt
from datetime import datetime, timezone
from uuid import UUID
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.configs import settings


def generate_permanent_token(user_id: str) -> str:
    """Generate a JWT token without expiration date"""
    try:
        # Validate UUID format
        user_uuid = UUID(user_id)
        
        # Create token payload without expiration
        to_encode = {
            "sub": str(user_uuid),
            "iat": datetime.now(timezone.utc),
            "permanent": True  # Flag to indicate this is a permanent token
        }
        
        # Generate token
        token = jwt.encode(
            to_encode,
            settings.jwt_token.JWT_SECRET_KEY,
            algorithm=settings.jwt_token.ALGORITHM
        )
        
        return token
        
    except ValueError as e:
        raise ValueError(f"Invalid UUID format: {user_id}")
    except Exception as e:
        raise Exception(f"Failed to generate token: {str(e)}")


def main():
    print("="*60)
    print("PERMANENT JWT TOKEN GENERATOR")
    print("="*60)
    print("This tool generates JWT tokens without expiration date.")
    print("WARNING: These tokens do not expire and should be used carefully!")
    print("="*60)
    
    while True:
        try:
            user_id = input("\nEnter User ID (UUID format): ").strip()
            
            if not user_id:
                print("Error: User ID cannot be empty!")
                continue
            
            if user_id.lower() in ['exit', 'quit', 'q']:
                print("Exiting...")
                sys.exit(0)
            
            token = generate_permanent_token(user_id)
            
            print("\n" + "="*60)
            print("PERMANENT JWT TOKEN GENERATED")
            print("="*60)
            print(f"User ID: {user_id}")
            print(f"Token: {token}")
            print("="*60)
            print("WARNING: This token does not expire!")
            print("Store it securely and revoke if compromised.")
            print("="*60)
            
            # Ask if user wants to generate another token
            another = input("\nGenerate another token? (y/n): ").strip().lower()
            if another not in ['y', 'yes']:
                print("Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please try again with a valid UUID format.")
            print("Example: b9667bcd-0a1a-4008-8d17-347d0606552f")
            continue


if __name__ == "__main__":
    main()
