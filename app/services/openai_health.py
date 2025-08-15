import logging
import time
from typing import Dict, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.core.configs import settings


class OpenAIHealthService:
    """Service for checking OpenAI API health and connectivity"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.openai.API_KEY)
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Comprehensive health check for OpenAI API
        
        Returns:
            dict: Health status with details
        """
        health_status = {
            "service": "openai",
            "status": "unknown",
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Check 1: API Key validation
        api_key_check = await self._check_api_key()
        health_status["checks"]["api_key"] = api_key_check
        
        # Check 2: Model availability
        model_check = await self._check_model_availability()
        health_status["checks"]["model"] = model_check
        
        # Check 3: Simple completion test
        completion_check = await self._check_completion()
        health_status["checks"]["completion"] = completion_check
        
        # Determine overall status
        all_checks_passed = all(
            check["status"] == "healthy" 
            for check in health_status["checks"].values()
        )
        
        health_status["status"] = "healthy" if all_checks_passed else "unhealthy"
        
        # Add summary
        health_status["summary"] = self._generate_summary(health_status)
        
        return health_status
    
    async def _check_api_key(self) -> Dict[str, Any]:
        """Check if API key is configured and valid"""
        check = {
            "name": "API Key",
            "status": "unknown",
            "details": {}
        }
        
        try:
            # Check if API key is configured
            if not settings.openai.API_KEY:
                check["status"] = "unhealthy"
                check["details"]["error"] = "OpenAI API key not configured"
                check["details"]["solution"] = "Set OPENAI_API_KEY environment variable"
                return check
            
            # Check API key format
            if not settings.openai.API_KEY.startswith(('sk-', 'sk-proj-')):
                check["status"] = "unhealthy"
                check["details"]["error"] = "Invalid API key format"
                check["details"]["solution"] = "Ensure API key starts with 'sk-' or 'sk-proj-'"
                return check
            
            check["status"] = "healthy"
            check["details"]["key_length"] = len(settings.openai.API_KEY)
            check["details"]["key_prefix"] = settings.openai.API_KEY[:7] + "..."
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["details"]["error"] = str(e)
            self.logger.error(f"API key check failed: {e}")
        
        return check
    
    async def _check_model_availability(self) -> Dict[str, Any]:
        """Check if configured model is available"""
        check = {
            "name": "Model Availability",
            "status": "unknown",
            "details": {}
        }
        
        try:
            # Try to list models to verify API access
            models = await self.client.models.list()
            
            # Check if our configured model is available
            available_models = [model.id for model in models.data]
            configured_model = settings.openai.MODEL
            
            if configured_model in available_models:
                check["status"] = "healthy"
                check["details"]["configured_model"] = configured_model
                check["details"]["model_available"] = True
            else:
                check["status"] = "unhealthy"
                check["details"]["configured_model"] = configured_model
                check["details"]["model_available"] = False
                check["details"]["error"] = f"Model '{configured_model}' not available"
                check["details"]["available_models"] = available_models[:10]  # Limit output
            
            check["details"]["total_models_available"] = len(available_models)
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["details"]["error"] = str(e)
            self.logger.error(f"Model availability check failed: {e}")
        
        return check
    
    async def _check_completion(self) -> Dict[str, Any]:
        """Test actual completion functionality"""
        check = {
            "name": "Completion Test",
            "status": "unknown",
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Simple test completion
            response = await self.client.chat.completions.create(
                model=settings.openai.MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Health check OK' in exactly 3 words."}
                ],
                max_tokens=10,
                temperature=0
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Validate response
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                check["status"] = "healthy"
                check["details"]["response_time_seconds"] = round(response_time, 3)
                check["details"]["test_response"] = content
                check["details"]["tokens_used"] = response.usage.total_tokens if response.usage else "unknown"
            else:
                check["status"] = "unhealthy"
                check["details"]["error"] = "Empty response from OpenAI"
            
        except Exception as e:
            check["status"] = "unhealthy"
            check["details"]["error"] = str(e)
            check["details"]["error_type"] = type(e).__name__
            self.logger.error(f"Completion test failed: {e}")
        
        return check
    
    def _generate_summary(self, health_status: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of health check results"""
        checks = health_status["checks"]
        
        healthy_checks = [name for name, check in checks.items() if check["status"] == "healthy"]
        unhealthy_checks = [name for name, check in checks.items() if check["status"] == "unhealthy"]
        
        summary = {
            "overall_status": health_status["status"],
            "total_checks": len(checks),
            "healthy_checks": len(healthy_checks),
            "unhealthy_checks": len(unhealthy_checks),
            "healthy_services": healthy_checks,
            "unhealthy_services": unhealthy_checks
        }
        
        if unhealthy_checks:
            # Collect errors for quick troubleshooting
            errors = []
            for check_name in unhealthy_checks:
                error = checks[check_name]["details"].get("error", "Unknown error")
                errors.append(f"{check_name}: {error}")
            summary["errors"] = errors
        
        return summary
    
    async def quick_check(self) -> bool:
        """
        Quick health check that returns just True/False
        Useful for simple monitoring
        """
        try:
            # Just test if we can make a simple API call
            response = await self.client.chat.completions.create(
                model=settings.openai.MODEL,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                temperature=0
            )
            return bool(response.choices and response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"Quick health check failed: {e}")
            return False


# Create service instance
openai_health_service = OpenAIHealthService()
