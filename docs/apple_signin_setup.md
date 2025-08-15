# Apple Sign In Setup Guide

## Current Status
The basic Apple Sign In infrastructure is implemented but requires additional configuration for production use.

## What's Already Implemented
- Database model with `apple_id` field
- API endpoint `/auth/apple-signin/`
- User registration/login flow
- JWT token generation

## Required Apple Developer Setup

### 1. Apple Developer Account Requirements
You need to configure the following in your Apple Developer Account:

#### A. Create App ID
1. Go to Apple Developer Console
2. Create new App ID with Sign In with Apple capability
3. Note the **Bundle ID** (this will be your CLIENT_ID)

#### B. Create Service ID (for web/backend)
1. Create new Service ID
2. Enable Sign In with Apple
3. Configure domains and redirect URLs
4. Note the **Service ID** (alternative CLIENT_ID for web)

#### C. Create Private Key
1. Go to Keys section
2. Create new key with Sign In with Apple capability
3. Download the `.p8` file
4. Note the **Key ID**

#### D. Get Team ID
1. Found in Apple Developer Account membership details

### 2. Environment Variables Required

Add these variables to your `.env` file:

```env
# Apple Sign In Configuration
APPLE_TEAM_ID=your_team_id_here
APPLE_KEY_ID=your_key_id_here
APPLE_CLIENT_ID=your_bundle_id_or_service_id
APPLE_PRIVATE_KEY_PATH=/path/to/your/private_key.p8
# OR store private key content directly:
APPLE_PRIVATE_KEY_CONTENT="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----"
```

### 3. Current Implementation Limitations

The current implementation accepts a simple `apple_id` string, but for production you need:

#### A. Token Validation Service
Create a service to:
- Validate Apple's `identityToken` 
- Verify JWT signature using Apple's public keys
- Extract user information securely

#### B. Required Dependencies
Add to `pyproject.toml`:
```toml
"cryptography>=41.0.0",  # For JWT signature verification
"requests>=2.31.0",      # For fetching Apple public keys
```

#### C. Schema Updates
Update `AppleSignIn` schema to accept identity token:
```python
class AppleSignIn(UserBase):
    identity_token: str      # JWT from Apple
    authorization_code: str  # For server-side validation
```

## Implementation Steps for Production

### 1. Add Dependencies
```bash
pip install cryptography requests
```

### 2. Create Apple Token Validation Service
Need to implement:
- Apple public key fetching
- JWT signature verification  
- User data extraction

### 3. Update Authentication Flow
- Validate incoming Apple tokens
- Extract verified user data
- Create/update user records

### 4. Security Considerations
- Store private keys securely
- Validate all incoming tokens
- Implement proper error handling
- Use HTTPS in production

## Testing

### Development Testing
Current implementation can be tested with any `apple_id` string, but this is NOT secure for production.

### Production Testing
Requires actual Apple Developer account and iOS/web client integration.

## Next Steps

1. **Immediate**: Set up Apple Developer account and get required keys
2. **Development**: Implement proper token validation
3. **Security**: Add signature verification
4. **Testing**: Test with real Apple Sign In flow

## Notes

- Current implementation is a foundation but NOT production-ready
- Real Apple Sign In requires cryptographic validation
- All Apple tokens must be verified server-side for security
- Consider rate limiting and abuse prevention
