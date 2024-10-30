from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from generator import PasswordGenerator

# Init
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
generator = PasswordGenerator()

# Default
@app.get("/", response_class=HTMLResponse)

async def root(request: Request):
    """Generate passwords and render them in a simple HTML page."""
    passwords = generator._generate_all_passwords()
    return templates.TemplateResponse(request=request, name="index.html", context={"passwords": passwords})

# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 8000))
#     uvicorn.run(app, host="0.0.0.0", port=port)
