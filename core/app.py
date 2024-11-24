import os
from .limiter import limiter
from .router import router
from .templates import templates
from .strings import get_random_rate_limit_warning
from .env import env_handler

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api_analytics.fastapi import Analytics

# Init
# https://fastapi.tiangolo.com/#example
app = FastAPI()

# Rate limiter
# https://slowapi.readthedocs.io/en/latest/#fastapi
app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) 

# Analytics
# https://pypi.org/project/fastapi-analytics/
app.add_middleware(Analytics, api_key=env_handler.analytics_key)

# Exception handlers
# https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc):
    """Custom handler for HTTPException"""
    blocks = str(exc).split(": ")
    return templates.TemplateResponse(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        name="exception.html",
        context={
            "detail": blocks[1],
        }
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, _: RateLimitExceeded):
    """Custom handler for RateLimitExceeded"""
    return templates.TemplateResponse(
        request=request,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        name="exception.html",
        context={
            "detail": get_random_rate_limit_warning(),
        },
    )

# Include password endpoints
app.include_router(router)

# Static files
# https://fastapi.tiangolo.com/tutorial/static-files/
# app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
