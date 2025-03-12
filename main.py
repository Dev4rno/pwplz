
import httpx

from core.strings import get_random_rate_limit_warning
from core.env import env_handler
from core.generator import PasswordGenerator, PasswordType

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi import Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from api_analytics.fastapi import Analytics
import logging
from collections import defaultdict
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plausible_proxy")

# Constants for the proxy
PLAUSIBLE_EVENT_URL = "https://plausible.io/api/event"
YOUR_DOMAIN = "pwplz.com"  # Change to your actual domain

# Path for the proxy - ensure this matches in your HTML!
PROXY_PATH = "/js"  # Using the path you're already requesting

# Simple in-memory cache for the script
script_cache = {
    "content": None,
    "timestamp": 0,
    "lock": threading.Lock()
}

# Basic rate limiting (per IP)
rate_limits = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10     # requests per window

async def rate_limit_exception_handler(request: Request, _: RateLimitExceeded):
    """Custom handler for RateLimitExceeded"""
    return templates.TemplateResponse(
        name="exception.html",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        context={"request": request, "detail": get_random_rate_limit_warning()},
    )


async def send_plausible_pageview(request: Request, path: str):
    """
    Send a pageview event to Plausible API from the server side
    """
    try:
        # Get client information
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else "127.0.0.1"
        referer = request.headers.get("referer", "")
        
        # Construct the full URL
        scheme = request.url.scheme  # http or https
        base_url = f"{scheme}://{YOUR_DOMAIN}"
        full_url = f"{base_url}{path}"
        
        # Prepare the payload
        payload = {
            "name": "pageview",
            "url": full_url,
            "domain": YOUR_DOMAIN
        }
        
        # Prepare headers
        headers = {
            "User-Agent": user_agent,
            "X-Forwarded-For": ip_address,
            "Content-Type": "application/json"
        }
        
        # Add referrer if available
        if referer:
            headers["Referer"] = referer
            
        # Send the request to Plausible
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                PLAUSIBLE_EVENT_URL,
                json=payload,
                headers=headers
            )
            
        if response.status_code == 202:
            logging.info(f"Plausible event sent successfully for {path}")
        else:
            logging.warning(f"Failed to send Plausible event: {response.status_code} - {response.text}")
            
    except Exception as e:
        logging.error(f"Error sending Plausible event: {str(e)}")

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
async def render_all_passwords(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Default endpoint to render a simple HTML page with all generated passwords"""
    try:
        background_tasks.add_task(send_plausible_pageview, request, "/")
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
async def render_single_password(
    request: Request, 
    slug: str,
    background_tasks: BackgroundTasks,
):
    """Endpoint to render a simple HTML page with a single method-specific password"""
    try:
        # Validate slug
        background_tasks.add_task(send_plausible_pageview, request, f"/{slug}")
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
    
