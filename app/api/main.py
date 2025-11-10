import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from config import settings
from domain.exceptions import (
    DomainValidationError,
    DuplicateCodeError,
    EntityNotFoundError,
    RelatedEntityExistsError,
)
from routers import city, country, state
from routers.utils import get_client_ip

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Country API",
    description="CRUD API for managing countries and states/provinces with event logging (Transactional Outbox pattern)",
    version="1.0.0",
)


# Global exception handlers
@app.exception_handler(DuplicateCodeError)
async def duplicate_code_error_handler(request: Request, exc: DuplicateCodeError):
    """Handle duplicate code errors (409 Conflict)"""
    logger.debug(
        "DuplicateCodeError: %s | Path: %s | Method: %s | IP: %s",
        exc.message,
        request.url.path,
        request.method,
        get_client_ip(request),
    )
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message},
    )


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_error_handler(request: Request, exc: EntityNotFoundError):
    """Handle entity not found errors (404 Not Found)"""
    logger.debug(
        "EntityNotFoundError: %s | Path: %s | Method: %s | IP: %s",
        exc.message,
        request.url.path,
        request.method,
        get_client_ip(request),
    )
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


@app.exception_handler(RelatedEntityExistsError)
async def related_entity_exists_error_handler(
    request: Request, exc: RelatedEntityExistsError
):
    """Handle related entity exists errors (400 Bad Request)"""
    logger.debug(
        "RelatedEntityExistsError: %s | Path: %s | Method: %s | IP: %s",
        exc.message,
        request.url.path,
        request.method,
        get_client_ip(request),
    )
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )


@app.exception_handler(DomainValidationError)
async def domain_validation_error_handler(request: Request, exc: DomainValidationError):
    """Handle other domain validation errors (400 Bad Request)"""
    logger.debug(
        "DomainValidationError: %s | Path: %s | Method: %s | IP: %s",
        exc.message,
        request.url.path,
        request.method,
        get_client_ip(request),
    )
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (500 Internal Server Error)"""
    logger.error(
        "IntegrityError: %s | Path: %s | Method: %s | IP: %s",
        str(exc),
        request.url.path,
        request.method,
        get_client_ip(request),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected database error occurred"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unexpected exceptions (500 Internal Server Error)"""
    logger.error(
        "Unexpected error: %s | Path: %s | Method: %s | IP: %s",
        str(exc),
        request.url.path,
        request.method,
        get_client_ip(request),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


# Register routers
app.include_router(country.router)
app.include_router(state.router)
app.include_router(city.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
