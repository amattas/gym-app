from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from gym_api.middleware.error_handler import (
    ErrorHandlerMiddleware,
    http_exception_handler,
    validation_exception_handler,
)
from gym_api.middleware.idempotency import IdempotencyMiddleware
from gym_api.middleware.request_id import RequestIDMiddleware
from gym_api.routers.health import router as health_router

app = FastAPI(title="Gym API", version="0.1.0")

# Middleware stack (outermost first — added last runs first)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(IdempotencyMiddleware)

# Exception handlers (for HTTPException/validation — caught before middleware)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Routers
app.include_router(health_router)
