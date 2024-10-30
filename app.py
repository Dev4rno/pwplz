import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from generator import PasswordGenerator

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
    return templates.TemplateResponse(
        request=request,
        name="exception.html",
        context={
            "status_code": status.HTTP_400_BAD_REQUEST,
            "detail": str(exc).replace(": ", " • ")
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
        context={"passwords": generator._generate_all_passwords()}
    )

##########################################>
# Method-specific route
@app.get("/{method}", response_class=HTMLResponse)
##########################################>

async def render_single_password(request: Request, method: str):
    """Endpoint to render a simple HTML page with a single generated password"""
    try:
        creator = generator._get_password_creation_method(method)
        return templates.TemplateResponse(
            request=request,
            name="single_password.html",
            context={
                "method": method,
                "password": creator(),
            }
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid password type: {method}",
        )