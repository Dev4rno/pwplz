
import httpx

from core.strings import get_random_rate_limit_warning
from core.env import env_handler
from core.generator import PasswordGenerator, PasswordType

from fastapi import FastAPI, Request, HTTPException, Response
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
PLAUSIBLE_SCRIPT_URL = "https://plausible.io/js/script.js"
PLAUSIBLE_EVENT_URL = "https://plausible.io/api/event"

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
    
def is_rate_limited(ip):
    """Check if an IP is being rate limited"""
    now = time.time()
    # Remove requests older than the window
    rate_limits[ip] = [t for t in rate_limits[ip] if now - t < RATE_LIMIT_WINDOW]
    # Check if too many requests
    if len(rate_limits[ip]) >= RATE_LIMIT_MAX:
        return True
    # Record this request
    rate_limits[ip].append(now)
    return False

@app.get(f"{PROXY_PATH}/script.js")
async def proxy_plausible_script(request: Request):
    """
    Proxy the Plausible script file with caching and rate limiting
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Check rate limiting
        if is_rate_limited(client_ip):
            logger.warning(f"Rate limiting client {client_ip}")
            return Response(
                content="console.log('Too many requests, please try again later');",
                status_code=429,
                media_type="application/javascript"
            )
            
        # Check cache first (with thread safety)
        with script_cache["lock"]:
            now = time.time()
            # If we have a recent cached version, return it
            if script_cache["content"] and (now - script_cache["timestamp"] < 86400):  # 24 hour cache
                logger.info("Serving Plausible script from cache")
                return Response(
                    content=script_cache["content"],
                    media_type="application/javascript",
                    headers={"Cache-Control": "public, max-age=86400"}
                )
            
            # Otherwise, fetch a new copy
            logger.info(f"Fetching fresh Plausible script from {PLAUSIBLE_SCRIPT_URL}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(PLAUSIBLE_SCRIPT_URL)
                
                if response.status_code == 200:
                    # Update cache
                    script_cache["content"] = response.content
                    script_cache["timestamp"] = now
                    
                # Return the response
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    media_type="application/javascript",
                    headers={"Cache-Control": "public, max-age=86400"}
                )
    except Exception as e:
        logger.error(f"Error proxying Plausible script: {e}")
        return Response(
            content=f"console.error('Error loading analytics: {str(e)}');",
            media_type="application/javascript",
            status_code=500
        )

@app.post(f"{PROXY_PATH}/event")
async def proxy_plausible_event(request: Request):
    """
    Proxy the Plausible API event endpoint
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Check rate limiting
        if is_rate_limited(client_ip):
            logger.warning(f"Rate limiting client {client_ip}")
            return Response(
                content="Too many requests",
                status_code=429,
                media_type="application/json"
            )
            
        # Get request body
        body = await request.json()
        logger.info(f"Proxying Plausible event: {body.get('name', 'unknown')}")
        
        # Forward necessary headers
        headers = {}
        for k, v in request.headers.items():
            if k.lower() not in ("host", "content-length", "connection", "content-encoding"):
                headers[k] = v
                
        # Make request to Plausible
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                PLAUSIBLE_EVENT_URL,
                json=body,
                headers=headers
            )
        
        # Return Plausible's response
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type", "application/json")
        )
    except Exception as e:
        logger.error(f"Error proxying Plausible event: {e}")
        return Response(
            content=f"Error: {str(e)}",
            status_code=500
        )        