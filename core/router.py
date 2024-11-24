import os
from core.generator import PasswordGenerator, PasswordType
from core.templates import templates
from core.limiter import limiter
from .env import env_handler

from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException

# Init
router = APIRouter()
generator = PasswordGenerator(
    words=env_handler.words,
    min_length=env_handler.min_length,
)

@router.get("/", response_class=HTMLResponse)
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
@router.get("/{slug}", response_class=HTMLResponse)
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
    