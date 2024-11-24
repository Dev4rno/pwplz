import os
from core.limiter import limiter
# from core.router import router
# from core.templates import templates
from core.strings import get_random_rate_limit_warning
from core.env import env_handler

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from api_analytics.fastapi import Analytics

# import os
from core.generator import PasswordGenerator, PasswordType
# from core.templates import templates
from core.limiter import limiter

from fastapi import Request, status
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException

from fastapi.templating import Jinja2Templates
# https://fastapi.tiangolo.com/advanced/templates/
templates = Jinja2Templates(directory="templates")

# Init
# https://fastapi.tiangolo.com/#example
app = FastAPI()

# Static files
# https://fastapi.tiangolo.com/tutorial/static-files/
app.mount("/static", StaticFiles(directory="static"), name="static")
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Rate limiter
# https://slowapi.readthedocs.io/en/latest/#fastapi
app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) 

# Analytics
# https://pypi.org/project/fastapi-analytics/
app.add_middleware(Analytics, api_key=env_handler.analytics_key)
app.add_middleware(SlowAPIMiddleware)

# Exception handlers
# https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc):
    """Custom handler for HTTPException"""
    # blocks = str(exc).split(": ")
    return templates.TemplateResponse(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        name="exception.html",
        context={
            "detail": exc,
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
# app.include_router(router)


generator = PasswordGenerator(
    words=env_handler.words,
    min_length=env_handler.min_length,
)

@app.get("/", response_class=HTMLResponse)
@limiter.limit(f"{env_handler.default_rate_limit}/minute")
async def render_all_passwords(request: Request):
    """Default endpoint to render a simple HTML page with all generated passwords"""
    try:
        return templates.TemplateResponse(
            request=request,
            name="all_passwords.html",
            context={
                "passwords": generator._generate_all_passwords(),
                "random_method": generator._get_random_password_type(),
            }
        )
    # Handle unexpected error
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong, try again later",
        )
    
# Method-specific route
@app.get("/{slug}", response_class=HTMLResponse)
@limiter.limit(f"{env_handler.advanced_rate_limit}/minute")
async def render_single_password(request: Request, slug: str):
    """Endpoint to render a simple HTML page with a single method-specific password"""
    try:
        # Validate slug
        password_type = PasswordType[slug.upper()]
        # Map slug to generator method 
        creator = generator._get_password_creation_method(password_type) 
        # Return the template with the generated password
        return templates.TemplateResponse(
            request=request,
            name="single_password.html",
            context={
                "slug": slug,
                "password": creator(),
            },
        )
    # Handle invalid slug
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid password type: {slug}",
        )
    