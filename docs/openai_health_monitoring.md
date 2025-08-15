# OpenAI Health Monitoring

## Overview
Comprehensive health monitoring for OpenAI API integration with detailed diagnostics and quick status checks.

## Available Endpoints

### 1. Comprehensive System Health Check
**GET** `/api/v1/health/`

Returns overall system status including all services.

**Response Example:**
```json
{
  "success": true,
  "message": "System status: healthy",
  "data": {
    "overall_status": "healthy",
    "timestamp": 1704723600.123,
    "services": {
      "application": {
        "status": "healthy",
        "message": "Application is running"
      },
      "database": {
        "status": "healthy",
        "connection_active": true
      },
      "openai": {
        "status": "healthy",
        "check_type": "quick"
      }
    }
  }
}
```

### 2. Comprehensive OpenAI Health Check
**GET** `/api/v1/health/openai/`

Detailed OpenAI API health check with multiple validation tests.

**Response Example:**
```json
{
  "success": true,
  "message": "OpenAI API status: healthy",
  "data": {
    "service": "openai",
    "status": "healthy",
    "timestamp": 1704723600.123,
    "checks": {
      "api_key": {
        "name": "API Key",
        "status": "healthy",
        "details": {
          "key_length": 51,
          "key_prefix": "sk-proj..."
        }
      },
      "model": {
        "name": "Model Availability",
        "status": "healthy",
        "details": {
          "configured_model": "gpt-4o-mini",
          "model_available": true,
          "total_models_available": 25
        }
      },
      "completion": {
        "name": "Completion Test",
        "status": "healthy",
        "details": {
          "response_time_seconds": 0.847,
          "test_response": "Health check OK",
          "tokens_used": 15
        }
      }
    },
    "summary": {
      "overall_status": "healthy",
      "total_checks": 3,
      "healthy_checks": 3,
      "unhealthy_checks": 0,
      "healthy_services": ["api_key", "model", "completion"],
      "unhealthy_services": []
    }
  }
}
```

### 3. Quick OpenAI Check
**GET** `/api/v1/health/openai/quick/`

Fast connectivity check for monitoring purposes.

**Response Example:**
```json
{
  "success": true,
  "message": "OpenAI API is responsive",
  "data": {
    "service": "openai",
    "status": "healthy",
    "check_type": "quick",
    "timestamp": 1704723600.123
  }
}
```

## Health Check Details

### API Key Validation
- ✅ Checks if `OPENAI_API_KEY` is configured
- ✅ Validates API key format (sk- or sk-proj- prefix)
- ✅ Reports key length and masked prefix

### Model Availability
- ✅ Lists available models from OpenAI
- ✅ Verifies configured model (`gpt-4o-mini`) is available
- ✅ Reports total number of available models

### Completion Test
- ✅ Performs actual API call with minimal tokens
- ✅ Measures response time
- ✅ Validates response content
- ✅ Reports token usage

## Error Handling

### Unhealthy Response Example
```json
{
  "success": false,
  "message": "OpenAI API status: unhealthy",
  "data": {
    "service": "openai",
    "status": "unhealthy",
    "timestamp": 1704723600.123,
    "checks": {
      "api_key": {
        "name": "API Key",
        "status": "unhealthy",
        "details": {
          "error": "OpenAI API key not configured",
          "solution": "Set OPENAI_API_KEY environment variable"
        }
      }
    },
    "summary": {
      "overall_status": "unhealthy",
      "total_checks": 3,
      "healthy_checks": 0,
      "unhealthy_checks": 1,
      "errors": ["api_key: OpenAI API key not configured"]
    }
  }
}
```

## Usage Examples

### cURL Commands
```bash
# Quick check
curl http://localhost:8080/api/v1/health/openai/quick/

# Comprehensive check  
curl http://localhost:8080/api/v1/health/openai/

# Overall system health
curl http://localhost:8080/api/v1/health/
```

### Python Monitoring Script
```python
import asyncio
import aiohttp

async def monitor_openai_health():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8080/api/v1/health/openai/quick/') as response:
            data = await response.json()
            
            if data['success']:
                print("✅ OpenAI API is healthy")
            else:
                print("❌ OpenAI API issues detected")
                print(data['message'])

# Run monitoring
asyncio.run(monitor_openai_health())
```

### Integration with Monitoring Tools

#### Prometheus Metrics
The health endpoints can be scraped by Prometheus for alerting:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'fairy-tales-health'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/api/v1/health/openai/quick/'
```

#### Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/v1/health/openai/quick/ || exit 1
```

## Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200  | Healthy | All checks passed |
| 503  | Unhealthy | One or more checks failed |

## Troubleshooting

### Common Issues

**API Key Not Configured**
```
Error: "OpenAI API key not configured"
Solution: Set OPENAI_API_KEY environment variable
```

**Invalid Model**
```
Error: "Model 'gpt-4o-mini' not available"
Solution: Check model name or OpenAI account access
```

**Network Issues**
```
Error: "Failed to connect to OpenAI API"
Solution: Check internet connectivity and firewall settings
```

**Rate Limiting**
```
Error: "Rate limit exceeded"
Solution: Implement backoff strategy or upgrade OpenAI plan
```

## Monitoring Best Practices

1. **Regular Checks**: Use quick check every 30 seconds
2. **Detailed Checks**: Run comprehensive check every 5 minutes
3. **Alerting**: Set up alerts for status changes
4. **Logging**: Monitor response times and error patterns
5. **Graceful Degradation**: Handle OpenAI outages gracefully

## Security Notes

- Health endpoints don't expose actual API keys
- Only key prefix is shown in responses
- No sensitive data is logged
- Rate limiting recommended for health endpoints
