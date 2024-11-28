from core.strings import get_random_rate_limit_warning
from core.env import env_handler
from core.generator import PasswordGenerator, PasswordType
from core.limiter import limiter

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi import Request, status
from fastapi.responses import HTMLResponse
from api_analytics.fastapi import Analytics
from fastapi.templating import Jinja2Templates
from slowapi import Limiter#, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

async def rate_limit_exception_handler(request: Request, _: RateLimitExceeded):
    """Custom handler for RateLimitExceeded"""
    return templates.TemplateResponse(
        name="exception.html",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        context={"request": request, "detail": get_random_rate_limit_warning()},
    )
    
limiter = Limiter(key_func=get_remote_address)

# https://fastapi.tiangolo.com/advanced/templates/
templates = Jinja2Templates(directory="templates")

# https://fastapi.tiangolo.com/#example
app = FastAPI()

# Rate limiter state
# https://slowapi.readthedocs.io/en/latest/#fastapi
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)#, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Static files
# https://fastapi.tiangolo.com/tutorial/static-files/
app.mount("/static", StaticFiles(directory="static"), name="static")

# Analytics
# https://pypi.org/project/fastapi-analytics/
app.add_middleware(Analytics, api_key=env_handler.analytics_key)

# Exception handlers
# https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc):
    return templates.TemplateResponse(
        name="exception.html",
        context={"request": request, "detail": exc},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

# Start PasswordGenerator
generator = PasswordGenerator(
    words=env_handler.words,
    min_length=env_handler.min_length,
)

# Default route
@app.get("/", response_class=HTMLResponse)
@limiter.limit("5/minute")
async def render_all_passwords(request: Request):
    """Default endpoint to render a simple HTML page with all generated passwords"""
    try:
        return templates.TemplateResponse(
            "all_passwords.html",
            {
                "request": request,
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
@limiter.limit("10/minute")
async def render_single_password(request: Request, slug: str):
    """Endpoint to render a simple HTML page with a single method-specific password"""
    try:
        # Validate slug
        password_type = PasswordType[slug.upper()]
        # Map slug to generator method 
        creator = generator._get_password_creation_method(password_type) 
        # Return the template with the generated password
        return templates.TemplateResponse(
            "single_password.html",
            {
                "request": request,
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
    