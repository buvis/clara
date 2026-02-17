from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from clara.config import get_settings
from clara.exceptions import ConflictError, ForbiddenError, NotFoundError
from clara.middleware import CSRFMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="CLARA", version="0.1.0")

    app.add_middleware(CSRFMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    from clara.auth.api import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    from clara.auth.vault_api import router as vault_router
    app.include_router(vault_router, prefix="/api/v1/vaults", tags=["vaults"])
    from clara.contacts.api import router as contacts_router
    app.include_router(
        contacts_router,
        prefix="/api/v1/vaults/{vault_id}/contacts",
        tags=["contacts"],
    )
    from clara.contacts.sub_api import (
        addresses_router,
        contact_tags_router,
        methods_router,
        pets_router,
        relationships_router,
        vault_tags_router,
    )
    app.include_router(
        methods_router,
        prefix="/api/v1/vaults/{vault_id}/contacts/{contact_id}/methods",
        tags=["contacts"],
    )
    app.include_router(
        addresses_router,
        prefix="/api/v1/vaults/{vault_id}/contacts/{contact_id}/addresses",
        tags=["contacts"],
    )
    app.include_router(
        relationships_router,
        prefix="/api/v1/vaults/{vault_id}/contacts/{contact_id}/relationships",
        tags=["contacts"],
    )
    app.include_router(
        pets_router,
        prefix="/api/v1/vaults/{vault_id}/contacts/{contact_id}/pets",
        tags=["contacts"],
    )
    app.include_router(
        contact_tags_router,
        prefix="/api/v1/vaults/{vault_id}/contacts/{contact_id}/tags",
        tags=["contacts"],
    )
    app.include_router(
        vault_tags_router,
        prefix="/api/v1/vaults/{vault_id}/tags",
        tags=["contacts"],
    )
    from clara.activities.api import router as activities_router
    app.include_router(
        activities_router,
        prefix="/api/v1/vaults/{vault_id}/activities",
        tags=["activities"],
    )
    from clara.notes.api import router as notes_router
    app.include_router(
        notes_router,
        prefix="/api/v1/vaults/{vault_id}/notes",
        tags=["notes"],
    )
    from clara.reminders.api import router as reminders_router
    app.include_router(
        reminders_router,
        prefix="/api/v1/vaults/{vault_id}/reminders",
        tags=["reminders"],
    )
    from clara.reminders.stay_in_touch_api import router as sit_router
    app.include_router(
        sit_router,
        prefix="/api/v1/vaults/{vault_id}/contacts/{contact_id}/stay_in_touch",
        tags=["stay-in-touch"],
    )
    from clara.tasks.api import router as tasks_router
    app.include_router(
        tasks_router,
        prefix="/api/v1/vaults/{vault_id}/tasks",
        tags=["tasks"],
    )
    from clara.journal.api import router as journal_router
    app.include_router(
        journal_router,
        prefix="/api/v1/vaults/{vault_id}/journal",
        tags=["journal"],
    )
    from clara.finance.gift_api import router as gifts_router
    app.include_router(
        gifts_router,
        prefix="/api/v1/vaults/{vault_id}/gifts",
        tags=["gifts"],
    )
    from clara.finance.debt_api import router as debts_router
    app.include_router(
        debts_router,
        prefix="/api/v1/vaults/{vault_id}/debts",
        tags=["debts"],
    )
    from clara.files.api import router as files_router
    app.include_router(
        files_router,
        prefix="/api/v1/vaults/{vault_id}/files",
        tags=["files"],
    )
    from clara.customization.template_api import router as templates_router
    app.include_router(
        templates_router,
        prefix="/api/v1/vaults/{vault_id}/templates",
        tags=["templates"],
    )
    from clara.customization.custom_field_api import router as custom_fields_router
    app.include_router(
        custom_fields_router,
        prefix="/api/v1/vaults/{vault_id}/custom-fields",
        tags=["custom-fields"],
    )
    from clara.integrations.api import router as import_export_router
    app.include_router(
        import_export_router,
        prefix="/api/v1/vaults/{vault_id}",
        tags=["import-export"],
    )

    return app


app = create_app()
