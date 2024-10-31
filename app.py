import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from generator import PasswordGenerator, PasswordType

# Env
load_dotenv()
MIN_LENGTH = int(os.getenv("MIN_LENGTH"))
DICEWARE_WORDS = os.getenv("DICEWARE_WORDS")

# Init
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
generator = PasswordGenerator(MIN_LENGTH, DICEWARE_WORDS)

# Exception handlers
@app.exception_handler(HTTPException)
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

##########################################>
# Default route
@app.get("/", response_class=HTMLResponse)
##########################################>

async def render_all_passwords(request: Request):
    """Endpoint to render a simple HTML page with all generated passwords"""
    return templates.TemplateResponse(
        request=request,
        name="all_passwords.html",
        context={
            "passwords": generator._generate_all_passwords(),
            "random_method": generator._get_random_password_type(),
        }
    )

##########################################>
# Method-specific route
@app.get("/{method}", response_class=HTMLResponse)
##########################################>

async def render_single_password(request: Request, method: str):
    """Endpoint to render a simple HTML page with a single generated password"""
    try:
        # Special handling for "argon2"
        if method.lower() == "argon2":
            password_type = PasswordType.ARGON2
        # For all other cases, ensure method is alphabetic before converting to enum
        elif method.isalpha():
            password_type = PasswordType[method.upper()]
        else:
            raise ValueError  # Trigger HTTPException below if invalid

        # Retrieve the creation method function from the generator
        creator = generator._get_password_creation_method(password_type)
        
        # Return the template with the generated password
        return templates.TemplateResponse(
            request=request,
            name="single_password.html",
            context={
                "method": method,
                "password": creator(),
            }
        )
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid password type: {method}",
        )