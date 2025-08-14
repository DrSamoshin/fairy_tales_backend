from fastapi.responses import JSONResponse
from typing import Any, Optional, List


def response(
    message: str = "something happened", 
    status_code: int = 200, 
    data: Optional[Any] = None,
    success: bool = True,
    errors: Optional[List[str]] = None,
    error_code: Optional[str] = None
) -> JSONResponse:
    content = {
        "success": success,
        "message": message,
    }
    
    if data is not None:
        content["data"] = data
    
    # For error responses, add errors and error_code
    if not success:
        content["errors"] = errors or []
        if error_code:
            content["error_code"] = error_code
        
    return JSONResponse(
        status_code=status_code,
        content=content
    )
