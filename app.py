import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from generator import PasswordGenerator
from starlette.requests import Request

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

# Default script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))