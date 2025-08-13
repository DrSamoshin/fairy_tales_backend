from fastapi.responses import JSONResponse
from typing import Any, Optional


def response(
    message: str = "something happened", 
    status_code: int = 200, 
    data: Optional[Any] = None,
    success: bool = True
) -> JSONResponse:
    content = {
        "success": success,
        "message": message,
    }
    
    if data is not None:
        content["data"] = data
        
    return JSONResponse(
        status_code=status_code,
        content=content
    )
