import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.configs import settings
from app.api.endpoints.v1 import (
    router_health,
    router_admin,
    router_migration,
    router_auth,
    router_stories,
    router_heroes,
    router_legal,
)

BASE_DIR = Path(__file__).resolve().parent
contents = os.listdir(BASE_DIR)
main_app = FastAPI(
    openapi_version=settings.app_data.openapi_version,
)

# Add CORS middleware
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # для Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if main_app.openapi_schema:
        return main_app.openapi_schema

    def fix_nullable(schema: dict):
        if isinstance(schema, dict):
            if (
                "anyOf" in schema
                and isinstance(schema["anyOf"], list)
                and len(schema["anyOf"]) == 2
            ):
                has_null = any(item.get("type") == "null" for item in schema["anyOf"])
                non_null = next(
                    (item for item in schema["anyOf"] if item.get("type") != "null"),
                    None,
                )

                if has_null and non_null and "type" in non_null:
                    schema["type"] = [non_null["type"], "null"]
                    if "format" in non_null:
                        schema["format"] = non_null["format"]
                    schema.pop("anyOf")

            for value in schema.values():
                fix_nullable(value)

        elif isinstance(schema, list):
            for item in schema:
                fix_nullable(item)

    openapi_schema = get_openapi(
        title=settings.app_data.title,
        version=settings.app_data.version,
        description=settings.app_data.description,
        routes=main_app.routes,
        openapi_version="3.1.0",
    )

    fix_nullable(openapi_schema)

    main_app.openapi_schema = openapi_schema
    return main_app.openapi_schema


main_app.openapi = custom_openapi

main_app.include_router(router_auth, prefix="/api/v1")
main_app.include_router(router_stories, prefix="/api/v1")
main_app.include_router(router_heroes, prefix="/api/v1")
main_app.include_router(router_legal, prefix="/api/v1")
main_app.include_router(router_health, prefix="/api/v1")

# admin
if settings.run.ADMIN_MODE:
    main_app.include_router(router_admin, prefix="/api/v1")
    main_app.include_router(router_migration, prefix="/api/v1")


logging.info("admin mode: %s", settings.run.ADMIN_MODE)
logging.info("starting FastAPI")
logging.info("DB url: %s", settings.data_base.get_db_url())
