from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from gym_api.middleware.cors import create_cors_middleware
from gym_api.middleware.error_handler import (
    ErrorHandlerMiddleware,
    http_exception_handler,
    validation_exception_handler,
)
from gym_api.middleware.idempotency import IdempotencyMiddleware
from gym_api.middleware.rate_limiter import RateLimiterMiddleware
from gym_api.middleware.request_id import RequestIDMiddleware
from gym_api.middleware.security_headers import SecurityHeadersMiddleware
from gym_api.routers.auth import router as auth_router
from gym_api.routers.clients import router as clients_router
from gym_api.routers.exercises import router as exercises_router
from gym_api.routers.gyms import router as gyms_router
from gym_api.routers.health import router as health_router
from gym_api.routers.measurements import router as measurements_router
from gym_api.routers.programs import router as programs_router
from gym_api.routers.trainers import router as trainers_router
from gym_api.routers.workouts import router as workouts_router

app = FastAPI(title="Gym API", version="0.1.0")

# CORS (must be added before other middleware)
create_cors_middleware(app)

# Middleware stack (outermost first — added last runs first)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(IdempotencyMiddleware)

# Exception handlers (for HTTPException/validation — caught before middleware)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(gyms_router)
app.include_router(clients_router)
app.include_router(trainers_router)
app.include_router(exercises_router)
app.include_router(programs_router)
app.include_router(workouts_router)
app.include_router(measurements_router)
