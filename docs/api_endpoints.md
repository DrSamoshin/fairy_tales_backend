# API Endpoints Documentation

## Overview
This document describes all available API endpoints in the Fairy Tales backend application and their request/response schemas.

**Base URL:** `http://localhost:8000/api/v1`

---

## Authentication Endpoints

### POST /auth/apple-signin/
**Description:** Register or login user with Apple Sign In

**Request Schema:** `AppleSignIn`
```json
{
    "apple_id": "string",                    // Apple user identifier
    "name": "string",                        // Display name from Apple/client
    "identity_token": "string" | null       // JWT token from Apple Sign In (optional)
}
```

**Response Schema:** `AuthResponse`
```json
{
    "success": true,
    "message": "Apple Sign In successful",
    "data": {
        "user": {
            "id": "uuid",                    // User UUID
            "is_active": true,
            "created_at": "2024-12-01T12:00:00Z"
        },
        "token": {
            "access_token": "jwt_token_string",
            "token_type": "bearer",
            "expires_in": 604800             // 7 days in seconds
        }
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Apple Sign In verification failed",
    "errors": ["Invalid Apple identity token"],
    "error_code": "INVALID_CREDENTIALS"
}
```

---

### POST /auth/refresh/
**Description:** Refresh access token for authenticated user

**Authentication:** Required (Bearer token)

**Request:** No body required

**Response Schema:** `AuthResponse` (same as apple-signin)

---

## Story Endpoints

### POST /stories/generate/
**Description:** Generate a complete fairy tale story

**Authentication:** Required (Bearer token)

**Request Schema:** `StoryGenerateRequest`
```json
{
    "story_name": "string",                  // Title of the story
    "hero_name": "string",                   // Name of the main character
    "age": 7,                               // Target age (3-16)
    "story_style": "Adventure",             // Adventure, Fantasy, Educational, Mystery
    "language": "en",                       // en, ru, es, fr, de
    "story_idea": "string",                 // Main plot description
    "story_length": 3,                      // 1-5 (1=very short, 3=medium, 5=very long)
    "child_gender": "girl"                  // boy, girl
}
```

**Response Schema:** `StoryResponse`
```json
{
    "success": true,
    "message": "Story generated successfully",
    "data": {
        "story": {
            "id": "uuid",
            "user_id": "uuid",
            "title": "string",               // story_name from request
            "content": "string",             // Generated story text
            "hero_name": "string",
            "age": 7,
            "story_style": "Adventure",
            "language": "en",
            "story_idea": "string",
            "story_length": 3,
            "child_gender": "girl",
            "created_at": "2024-12-01T12:00:00Z"
        }
    }
}
```

---

### POST /stories/generate-stream/
**Description:** Generate a fairy tale story with streaming response (Server-Sent Events)

**Authentication:** Required (Bearer token)

**Request Schema:** `StoryGenerateRequest` (same as generate/)

**Response:** Server-Sent Events stream
```
Content-Type: text/plain
Cache-Control: no-cache
Connection: keep-alive

data: {"type": "started", "message": "Starting generation of 'Story Name'"}

data: {"type": "content", "content": "Once upon a time"}

data: {"type": "content", "content": " there was a brave"}

data: {"type": "complete", "message": "Story generation completed", "story_id": "uuid"}

data: {"type": "error", "message": "Generation failed: error details"}
```

**Stream Message Types:**
- `started` - Generation begins
- `content` - Story content chunks
- `complete` - Generation finished with story_id
- `error` - Error occurred during generation

---

### GET /stories/
**Description:** Get all stories for the authenticated user

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `skip`: Number of stories to skip (default: 0)
- `limit`: Maximum stories to return (default: 20, max: 100)

**Response Schema:** `StoriesListResponse`
```json
{
    "success": true,
    "message": "Stories retrieved successfully",
    "data": {
        "stories": [
            {
                "id": "uuid",
                "user_id": "uuid",
                "title": "string",
                "content": "string",
                "hero_name": "string",
                "age": 7,
                "story_style": "Adventure",
                "language": "en",
                "story_idea": "string",
                "story_length": 3,
                "child_gender": "girl",
                "created_at": "2024-12-01T12:00:00Z"
            }
        ],
        "total": 25,                         // Total stories count
        "skip": 0,
        "limit": 20
    }
}
```

---

### DELETE /stories/{story_id}/
**Description:** Delete a story (soft delete)

**Authentication:** Required (Bearer token)

**Path Parameters:**
- `story_id`: UUID of the story to delete

**Response Schema:** `BaseResponse`
```json
{
    "success": true,
    "message": "Story deleted successfully",
    "data": null
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Story not found",
    "errors": ["Story does not exist or you don't have permission to delete it"],
    "error_code": "STORY_NOT_FOUND"
}
```

---

## Admin Endpoints

### GET /admin/users/
**Description:** Get all users in the system (admin only)

**Authentication:** Required (Bearer token - simple token validation without DB lookup)

**Query Parameters:**
- `skip`: Number of users to skip (default: 0)
- `limit`: Maximum users to return (default: 100, max: 1000)

**Response Schema:** `UsersListResponse`
```json
{
    "success": true,
    "message": "Retrieved 25 users",
    "data": {
        "users": [
            {
                "id": "uuid",
                "apple_id": "string",
                "email": "string" | null,
                "is_active": true,
                "created_at": "2024-12-01T12:00:00Z"
            }
        ],
        "total": 100,
        "skip": 0,
        "limit": 25
    }
}
```

---

### GET /admin/stories/
**Description:** Get all stories in the system (admin only)

**Authentication:** Required (Bearer token - simple token validation without DB lookup)

**Query Parameters:**
- `skip`: Number of stories to skip (default: 0)
- `limit`: Maximum stories to return (default: 100, max: 1000)

**Response Schema:** `StoriesListResponse`
```json
{
    "success": true,
    "message": "Retrieved 50 stories",
    "data": {
        "stories": [...],                    // Array of StoryOut objects
        "pagination": {
            "skip": 0,
            "limit": 50,
            "count": 50,
            "total": 150
        }
    }
}
```

---

## Legal Endpoints

### GET /legal/policy-ios/
**Description:** Get iOS privacy policy

**Authentication:** None

**Response Schema:** `PolicyResponse`
```json
{
    "success": true,
    "message": "iOS policy retrieved successfully",
    "data": {
        "policy": "# Privacy Policy\n\n**Effective date:** 2024-12-01\n\n..."
    }
}
```

---

### GET /legal/terms/
**Description:** Get Terms of Use

**Authentication:** None

**Response Schema:** `PolicyResponse`
```json
{
    "success": true,
    "message": "Terms of Use retrieved successfully",
    "data": {
        "terms": "# Terms of Use\n\n**Effective date:** 2024-12-01\n\n..."
    }
}
```

---

## Health Endpoints

### GET /health/app/
**Description:** Application health check

**Authentication:** None

**Response Schema:** `BaseResponse`
```json
{
    "success": true,
    "message": "Application is running",
    "data": {
        "status": "healthy",
        "service": "fairy_tales_backend"
    }
}
```

---

### GET /health/openai/quick/
**Description:** Quick OpenAI API connectivity check

**Authentication:** Required (Bearer token - simple token validation without DB lookup)

**Response Schema:** `BaseResponse`
```json
{
    "success": true,
    "message": "OpenAI API is responsive",
    "data": {
        "service": "openai",
        "status": "healthy",
        "check_type": "quick",
        "timestamp": 1701432000
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "OpenAI API is not responsive",
    "data": {
        "service": "openai",
        "status": "unhealthy",
        "check_type": "quick",
        "timestamp": 1701432000
    }
}
```

---

## Common Response Schemas

### BaseResponse
```json
{
    "success": boolean,
    "message": "string"
}
```

### Error Response Format
```json
{
    "success": false,
    "message": "Error description",
    "errors": ["Detailed error messages"],
    "error_code": "ERROR_CODE_CONSTANT"
}
```

---

## Data Types and Enums

### StoryStyle Enum
- `Adventure`
- `Fantasy` 
- `Educational`
- `Mystery`

### Language Enum
- `en` - English
- `ru` - Russian
- `es` - Spanish
- `fr` - French
- `de` - German

### StoryLength Enum
- `1` - Very short (100-200 words)
- `2` - Short (200-300 words)
- `3` - Medium (300-400 words)
- `4` - Long (400-500 words)
- `5` - Very long (500-600 words)

### ChildGender Enum
- `boy`
- `girl`

---

## Error Codes

### Authentication Errors
- `INVALID_CREDENTIALS` - Invalid Apple identity token
- `UNAUTHORIZED` - Missing or invalid JWT token

### Story Errors
- `STORY_GENERATION_FAILED` - Failed to generate story
- `STORY_NOT_FOUND` - Story doesn't exist or no permission

### System Errors
- `INTERNAL_ERROR` - Internal server error
- `VALIDATION_ERROR` - Request validation failed

---

## Notes

1. **Authentication:** Most endpoints require a Bearer token in the Authorization header
2. **Content-Type:** All requests should use `application/json`
3. **Rate Limiting:** Story generation endpoints may have rate limiting applied
4. **Streaming:** The `/stories/generate-stream/` endpoint uses Server-Sent Events
5. **Soft Delete:** Stories are soft-deleted (marked as deleted, not physically removed)
6. **Apple Sign In:** Only authentication method supported
7. **Story Storage:** All stories are stored with full metadata and generated content
