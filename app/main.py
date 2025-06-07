from fastapi import FastAPI, Request
from app.api.router.listings import router as listings_router
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.exceptions import RequestValidationError

from app.api.exceptions.exceptions import NotFoundException

app = FastAPI(
    title="Listings API",
    description="API to retrieve filtered listings with properties and dataset entities.",
    version="1.0.0"
)

# include the listings endpoint
app.include_router(listings_router, prefix="/api", tags=["Listings"])


## General error handling

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )

@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"error": "Database error", "detail": str(exc)},
    )

@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Not Found", "detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "details": exc.errors()},
    )