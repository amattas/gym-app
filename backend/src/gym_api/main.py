import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from gym_api.cache.cache_service import close_redis
from gym_api.config import settings
from gym_api.jobs.scheduler import setup_scheduler
from gym_api.metrics.prometheus import setup_metrics
from gym_api.middleware.cors import create_cors_middleware
from gym_api.middleware.error_handler import (
    ErrorHandlerMiddleware,
    http_exception_handler,
    validation_exception_handler,
)
from gym_api.middleware.https_redirect import create_https_redirect_middleware
from gym_api.middleware.idempotency import IdempotencyMiddleware
from gym_api.middleware.rate_limiter import RateLimiterMiddleware
from gym_api.middleware.request_id import RequestIDMiddleware
from gym_api.middleware.security_headers import SecurityHeadersMiddleware
from gym_api.routers.accounts import router as accounts_router
from gym_api.routers.agreements import router as agreements_router
from gym_api.routers.ai_summaries import router as ai_summaries_router
from gym_api.routers.analytics import router as analytics_router
from gym_api.routers.audit_logs import router as audit_logs_router
from gym_api.routers.auth import router as auth_router
from gym_api.routers.billing import router as billing_router
from gym_api.routers.calendar import router as calendar_router
from gym_api.routers.check_ins import router as check_ins_router
from gym_api.routers.clients import router as clients_router
from gym_api.routers.custom_domains import router as custom_domains_router
from gym_api.routers.data_privacy import router as data_privacy_router
from gym_api.routers.exercises import router as exercises_router
from gym_api.routers.goals import router as goals_router
from gym_api.routers.graphql_router import router as graphql_router
from gym_api.routers.gyms import router as gyms_router
from gym_api.routers.health import router as health_router
from gym_api.routers.invitations import router as invitations_router
from gym_api.routers.locations import location_detail_router
from gym_api.routers.locations import router as locations_router
from gym_api.routers.measurements import (
    client_measurements_router,
)
from gym_api.routers.measurements import (
    router as measurements_router,
)
from gym_api.routers.memberships import router as memberships_router
from gym_api.routers.notes import router as notes_router
from gym_api.routers.notifications import router as notifications_router
from gym_api.routers.plan_templates import router as plan_templates_router
from gym_api.routers.programs import router as programs_router
from gym_api.routers.progress_photos import router as progress_photos_router
from gym_api.routers.schedules import router as schedules_router
from gym_api.routers.stripe_webhooks import router as stripe_webhooks_router
from gym_api.routers.trainers import router as trainers_router
from gym_api.routers.usage import router as usage_router
from gym_api.routers.webhook_endpoints import router as webhook_endpoints_router
from gym_api.routers.workouts import router as workouts_router
from gym_api.utils.log_redaction import PiiRedactionFilter


def _setup_logging() -> None:
    pii_filter = PiiRedactionFilter()
    for handler in logging.root.handlers:
        handler.addFilter(pii_filter)
    if not logging.root.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(pii_filter)
        logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_jwt_secret()
    _setup_logging()
    sched = setup_scheduler()
    sched.start()
    logging.getLogger(__name__).info("Scheduler started")
    yield
    sched.shutdown(wait=False)
    await close_redis()
    logging.getLogger(__name__).info("Shutdown complete")


app = FastAPI(title="Gym API", version="0.1.0", lifespan=lifespan)

# CORS (must be added before other middleware)
create_cors_middleware(app)

# Metrics
setup_metrics(app)

# HTTPS redirect (enabled via ENFORCE_HTTPS=true)
create_https_redirect_middleware(app)

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
app.include_router(client_measurements_router)
app.include_router(invitations_router)
app.include_router(analytics_router)
app.include_router(plan_templates_router)
app.include_router(memberships_router)
app.include_router(locations_router)
app.include_router(location_detail_router)
app.include_router(schedules_router)
app.include_router(check_ins_router)
app.include_router(goals_router)
app.include_router(notes_router)
app.include_router(audit_logs_router)
app.include_router(progress_photos_router)
app.include_router(webhook_endpoints_router)
app.include_router(accounts_router)
app.include_router(notifications_router)
app.include_router(calendar_router)
app.include_router(ai_summaries_router)
app.include_router(data_privacy_router)
app.include_router(billing_router)
app.include_router(stripe_webhooks_router)
app.include_router(agreements_router)
app.include_router(usage_router)
app.include_router(custom_domains_router)
app.include_router(graphql_router)
