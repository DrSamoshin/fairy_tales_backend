from fastapi.responses import JSONResponse


def response(
    message: str = "something happened", status_code: int = 200, status: str = "success"
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "message": message,
        },
    )
