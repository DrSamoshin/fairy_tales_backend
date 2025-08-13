import logging
import subprocess
from fastapi import APIRouter, Depends
from app.core.responses import response
from app.services.authentication import get_user_id_from_token

router = APIRouter(prefix="/migration", tags=["migration"])


@router.get("/migrate-db/")
def migrate_db(user_id: str = Depends(get_user_id_from_token)):
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )
        logging.info(result)
        return response("db is migrated", 200, "success")
    except subprocess.CalledProcessError as e:
        return response("db is not migrated", 500, f"error: {str(e)}")
