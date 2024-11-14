import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from generator import PasswordGenerator, PasswordType
# from apitally.fastapi import ApitallyMiddleware
from api_analytics.fastapi import Analytics

# Env
load_dotenv()
API_ANALYTICS_KEY={os.getenv("API_ANALYTICS_KEY")}
APITALLY_ID = os.getenv("APITALLY_ID")
MIN_LENGTH = int(os.getenv("MIN_LENGTH"))
DICEWARE_WORDS = os.getenv("DICEWARE_WORDS")
generator = PasswordGenerator(min_length=MIN_LENGTH, words=DICEWARE_WORDS)

# Init
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#-=-=-=-=-=-=-=-=-=-=-=-=>
# Analytics via https://pypi.org/project/fastapi-analytics/
# configured with API_ANALYTICS_KEY (.env)
#-=-=-=-=-=-=-=-=-=-=-=-=>
app.add_middleware(
    Analytics, 
    api_key=API_ANALYTICS_KEY,
    # ApitallyMiddleware,
    # client_id=APITALLY_ID,
    # env="prod",
)

#-=-=-=-=-=-=-=-=-=-=-=-=>
# Exception wrapper
@app.exception_handler(HTTPException)
#-=-=-=-=-=-=-=-=-=-=-=-=>

async def validation_exception_handler(request: Request, exc):
    blocks = str(exc).split(": ")
    return templates.TemplateResponse(
        request=request,
        name="exception.html",
        context={
            "status_code": status.HTTP_400_BAD_REQUEST,
            "detail": blocks[1],
        }
    )

#-=-=-=-=-=-=-=-=-=-=-=-=>
# Default route
@app.get("/", response_class=HTMLResponse)
#-=-=-=-=-=-=-=-=-=-=-=-=>

async def render_all_passwords(request: Request):
    """Endpoint to render a simple HTML page with all generated passwords"""
    try:        
        return templates.TemplateResponse(
            request=request,
            name="all_passwords.html",
            context={
                "passwords": generator._generate_all_passwords(),
                "random_method": generator._get_random_password_type(),
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong, try again later",
        )
        
#-=-=-=-=-=-=-=-=-=-=-=-=>
# Method-specific route
@app.get("/{slug}", response_class=HTMLResponse)
#-=-=-=-=-=-=-=-=-=-=-=-=>

async def render_single_password(request: Request, slug: str):
    """Endpoint to render a simple HTML page with a single generated password"""
    try:
        # Validate slug in PasswordType 
        password_type = PasswordType[slug.upper()]
        
        # Map slug to password creation method 
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
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid password type: {slug}",
        )