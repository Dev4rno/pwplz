from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from generator import PasswordGenerator

# Init
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
generator = PasswordGenerator()

# Default
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Generate passwords and render them in a simple HTML page."""
    passwords = generator._generate_all_passwords()
    return templates.TemplateResponse("index.html", {"request": request, "passwords": passwords})